#!/usr/bin/env python


import rospy
import geometry_msgs.msg
from std_msgs.msg import String
import tf

class vmap_coordinate:
	def __init__(self):
		rospy.init_node('vmap_broadcaster', anonymous = False)
		rospy.Subscriber('mark_vmap', String, self.mark_vmap)

		self.t = geometry_msgs.msg.TransformStamped()
		self.marked = False
		return

	def mark_vmap(self, msg):
		if msg.data == "mark":
			self.mark()

	def mark(self):
		listener = tf.TransformListener()
		try:
			listener.waitForTransform("/base_link", "/odom", rospy.Time(0),rospy.Duration(4.0)) # TODO: odom or map?
			[trans,rot] = listener.lookupTransform("/odom", "/base_link", rospy.Time(0))
		except rospy.ROSInterruptException:
			return
		except Exception as e:
			rospy.logerr("Vmap_broadcaster: Cannot get the Transform!\nDetails: %s", e)
			return
		self.t = geometry_msgs.msg.TransformStamped()
		self.t.header.frame_id = 'odom'
		self.t.header.stamp = rospy.Time.now()
		self.t.child_frame_id = 'vmap'
		self.t.transform.translation.x = trans[0]
		self.t.transform.translation.y = trans[1]
		self.t.transform.translation.z = trans[2]
		self.t.transform.rotation.x = rot[0]
		self.t.transform.rotation.y = rot[1]
		self.t.transform.rotation.z = rot[2]
		self.t.transform.rotation.w = rot[3]
		self.marked = True

	def start(self):
		m = tf.TransformBroadcaster()
		self.mark()
		rate = rospy.Rate(1)
		while not rospy.is_shutdown():
			if self.marked:
				self.t.header.stamp = rospy.Time.now()
				m.sendTransformMessage(self.t)
			rate.sleep()

if __name__ == '__main__':  
	try:
		vmap = vmap_coordinate()
		vmap.start()
	except rospy.ROSInterruptException:
		pass