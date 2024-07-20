
import struct
import hl2ss


# 3D Primitive Types
class PrimitiveType:
    Sphere = 0
    Capsule = 1
    Cylinder = 2
    Cube = 3
    Plane = 4
    Quad = 5


# Server Target Mode
class TargetMode:
    UseID = 0
    UseLast = 1


# Object Active State
class ActiveState:
    Inactive = 0
    Active = 1


#------------------------------------------------------------------------------
# Commands
#------------------------------------------------------------------------------

class command_buffer(hl2ss.umq_command_buffer):
    def create_primitive(self, type):
        self.add(0, struct.pack('<I', type))

    def set_active(self, key, state):
        self.add(1, struct.pack('<II', key, state))

    def set_world_transform(self, key, position, rotation, scale):
        self.add(2, struct.pack('<Iffffffffff', key, position[0], position[1], position[2], rotation[0], rotation[1], rotation[2], rotation[3], scale[0], scale[1], scale[2]))

    def set_local_transform(self, key, position, rotation, scale):
        self.add(3, struct.pack('<Iffffffffff', key, position[0], position[1], position[2], rotation[0], rotation[1], rotation[2], rotation[3], scale[0], scale[1], scale[2]))

    def set_color(self, key, rgba):
        self.add(4, struct.pack('<Iffff', key, rgba[0], rgba[1], rgba[2], rgba[3]))

    def set_texture(self, key, texture):
        self.add(5, struct.pack('<I', key) + texture)

    def create_text(self): 
        self.add(6, b'')

    def set_text(self, key, font_size, rgba, string):
        self.add(7, struct.pack('<Ifffff', key, font_size, rgba[0], rgba[1], rgba[2], rgba[3]) + string.encode('utf-8'))

    def say(self, text):
        self.add(8, text.encode('utf-8'))

    def load_mesh(self, data):
        self.add(15, data)

    def remove(self, key):
        self.add(16, struct.pack('<I', key))

    def remove_all(self):
        self.add(17, b'')

    def begin_display_list(self):
        self.add(18, b'')

    def end_display_list(self):
        self.add(19, b'')

    def set_target_mode(self, mode):
        self.add(20, struct.pack('<I', mode))

    def create_arrow(self,index):
        self.add(21, struct.pack('<I', index)) #streaming index so we can set it as child of the corresponding path guidance group
    def send_dino_detection(self, type):
        self.add(22, struct.pack('<I', type))

    def check_done(self):
        self.add(23, b'')

    def create_point_cloud_renderer(self, detections, index):
        self.add(24, struct.pack('<I', detections) + struct.pack('<I', index))  #streaming index so we can set it as child of the corresponding path guidance group

    def send_point_cloud(self,len, point_cloud):
        self.add(25, struct.pack('<I', len)+ point_cloud.tobytes())

    def get_target_pos(self,target_index,axis):
        self.add(26, struct.pack('<I', target_index) + struct.pack('<I', axis))

    def change_table_scale(self,ratio):
        self.add(27, struct.pack('<I', ratio))

    def create_line_renderer(self, index):
            self.add(28, struct.pack('<I', index))  #streaming index so we can set it as child of the corresponding path guidance group
    def send_path_points(self,len, path_points):
        self.add(29, struct.pack('<I', len)+ path_points.tobytes())

    def get_target_corner_pos(self,target_index,corner, axis):
        self.add(30, struct.pack('<I', target_index) + struct.pack('<I', corner) + struct.pack('<I', axis))



