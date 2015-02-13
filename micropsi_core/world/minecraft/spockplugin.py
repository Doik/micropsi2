import logging
from spock.mcp import mcdata
from spock.mcp.mcpacket import Packet
from spock.utils import pl_announce
from spock.mcmap import mapdata
import math


STANCE_ADDITION = 1.620
STEP_LENGTH = 0.5
JUMPING_MAGIC_NUMBER = 0  # 2 used to work


@pl_announce('Micropsi')
class MicropsiPlugin(object):

    def __init__(self, ploader, settings):

        # register required plugins
        self.net = ploader.requires('Net')
        self.event = ploader.requires('Event')
        self.world = ploader.requires('World')
        self.clientinfo = ploader.requires('ClientInfo')
        self.threadpool = ploader.requires('ThreadPool')

        self.inventory = []
        self.quickslots = []

        self.event.reg_event_handler(
            (3, 0, 48),
            self.update_inventory
        )

        # make references between micropsi world and MicropsiPlugin
        self.micropsi_world = settings['micropsi_world']
        self.micropsi_world.spockplugin = self

    def chat(self, message):
        # else push chat message
        self.net.push(Packet(ident='PLAY>Chat Message', data={'message': message}))

    def is_connected(self):
        return self.net.connected and self.net.proto_state

    def dispatchMovement(self, move_x, move_z):
        target_coords = self.get_coordinates()

        # move +/- STEP_LENGTH, depending on parameter signedness
        if move_x:
            target_coords['x'] += math.copysign(STEP_LENGTH, move_x)
        if move_z:
            target_coords['z'] += math.copysign(STEP_LENGTH, move_z)

        # avoid standing on block edges for easier calculation
        if target_coords['x'] % 0.5 == 0:
            target_coords['x'] = round(target_coords['x'] - 0.1, 4)
        if target_coords['z'] % 0.5 == 0:
            target_coords['z'] = round(target_coords['z'] - 0.1, 4)

        # collect target blocks (1): block at coordinates
        block_coords = [self.get_block_coordinates(target_coords)]

        # collect target blocks (2): blocks we can are too close to:
        # since Steve is a fatty, movement is influenced by surrounding blocks if distance is smaller than 0.3
        dist = {
            'x': round((abs(target_coords['x']) % 1), 4),
            'z': round((abs(target_coords['z']) % 1), 4)
        }
        if not 0.3 <= dist['x'] <= 0.7 or not 0.3 <= dist['z'] <= 0.7:
            # we are too close to the next block, need to check that one too:
            for direction in ['x', 'z']:
                if dist[direction] < 0.3:
                    block_coords.append(self.get_block_coordinates(target_coords))
                    block_coords[-1][direction] -= int(math.copysign(1, target_coords[direction]))
                elif dist[direction] > 0.7:
                    block_coords.append(self.get_block_coordinates(target_coords))
                    block_coords[-1][direction] += int(math.copysign(1, target_coords[direction]))

        # collect ground offsets for every block we need to check
        ground_offset = []
        y = target_coords['y'] - 1  # this is the current block the agent is standing on

        # check movement possibility for every block
        for check_block in block_coords:
            move = False
            # print('checking block %d / %d / %d' % (check_block['x'], check_block['y'], check_block['z']))
            # check if the next step is possible: nothing in the way, height diff <= 1
            if self.is_opaque(self.get_block_type(check_block['x'], y + 2, check_block['z'])):
                move = False
            elif self.is_opaque(self.get_block_type(check_block['x'], y + 1, check_block['z'])) and \
                    not self.is_opaque(self.get_block_type(check_block['x'], y + 3, check_block['z'])):
                # check if we got a special block with height > 1 that we can not jump onto
                # (Door, IronDoor, Fence, Fence Gate, Cobblestone Wall)
                if self.get_block_type(check_block['x'], y + 1, check_block['z']) not in [64, 71, 85, 107, 139]:
                    ground_offset.append(1)
                    move = True
            elif self.is_opaque(self.get_block_type(check_block['x'], y, check_block['z'])):
                ground_offset.append(0)
                move = True
            elif self.is_opaque(self.get_block_type(check_block['x'], y - 1, check_block['z'])):
                ground_offset.append(-1)
                move = True
            if not move:
                print('nope')
                return False

        # take the highest block
        # (necessary, if we're close to other blocks)
        ground_offset.sort()
        ground_offset = ground_offset[-1]

        # TODO: what block do we use as standing on here?
        block_coords = block_coords[-1]

        # check for water:
        foot_block = self.get_block_type(block_coords['x'], y + 1, block_coords['z'])
        ground_block = self.get_block_type(block_coords['x'], y, block_coords['z'])
        if ground_block in [8, 9]:
            if foot_block in [8, 9]:
                # we're already swimming
                ground_offset = 0
            else:
                # we would be walking on water, adjust y to be *in* water
                ground_offset = -1

        # update our position
        self.clientinfo.position['x'] = target_coords['x']
        self.clientinfo.position['y'] = target_coords['y'] + ground_offset
        self.clientinfo.position['stance'] = target_coords['y'] + ground_offset + STANCE_ADDITION
        self.clientinfo.position['z'] = target_coords['z']
        self.clientinfo.position['on_ground'] = True
        return True

    def is_opaque(self, block_id):
        if block_id <= 0:
            return False
        if block_id in mapdata.blocks_dict:
            return mapdata.blocks_dict[block_id]['bounding_box'] != 'empty'
        return True

    def get_block_type(self, x, y, z):
        """
        Get the block type of a particular voxel.
        """
        x, y, z = int(x), int(y), int(z)
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if y > 0x0F:
            return -1  # was 0
        try:
            column = self.world.columns[(x, z)]
            chunk = column.chunks[y]
        except KeyError:
            return -1

        if chunk is None:
            return -1  # was 0
        return chunk.block_data.get(rx, ry, rz) >> 4

    def get_biome_info(self, pos=None):
        if pos is None:
            pos = self.get_block_coordinates()
        key = (pos['x'] // 16, pos['z'] // 16)
        columns = self.world.columns
        if key not in columns:
            return None
        current_column = columns[key]
        biome_id = current_column.biome.get(pos['x'] % 16, pos['z'] % 16)
        if biome_id >= 0:
            return mapdata.biomes[biome_id]
        else:
            return None

    def get_temperature(self, pos=None):
        if pos is None:
            pos = self.get_block_coordinates()
        biome = self.get_biome_info(pos=pos)
        if biome:
            temp = biome['temperature']
            if pos['y'] > 64:
                temp -= (0.00166667 * (pos['y'] - 64))
            return temp
        else:
            return None

    def eat(self):
        """ Attempts to eat the held item. Assumes held item implements eatable """
        logging.getLogger('world').debug('eating a bread')
        data = {
            'location': self.get_coordinates(cast_int=True),
            'direction': -1,
            'held_item': {
                'id': 297,
                'amount': 1,
                'damage': 0
            },
            'cur_pos_x': -1,
            'cur_pos_y': -1,
            'cur_pos_z': -1
        }
        self.net.push(Packet(ident='PLAY>Player Block Placement', data=data))

    def give_item(self, item, amount=1):
        message = "/item %s %d" % (str(item), amount)
        self.net.push(Packet(ident='PLAY>Chat Message', data={'message': message}))

    def update_inventory(self, event, packet):
        self.inventory = packet.data['slots']
        self.quickslots = packet.data['slots'][36:9]

    def count_inventory_item(self, item):
        count = 0
        for slot in self.inventory:
            if slot and slot['id'] == item:
                count += slot['amount']
        return count

    def change_held_item(self, target_slot):
        """ Changes the held item to a quick inventory slot """
        self.net.push(Packet(ident='PLAY>Held Item Change', data={'Slot': target_slot}))

    def move(self, position=None):
        if not (self.net.connected and self.net.proto_state == mcdata.PLAY_STATE):
            return
        # writes new data to clientinfo which is pulled and pushed to Minecraft by ClientInfoPlugin
        self.clientinfo.position = position

    def get_coordinates(self, cast_int=False):
        x = int(self.clientinfo.position['x']) if cast_int else self.clientinfo.position['x']
        z = int(self.clientinfo.position['z']) if cast_int else self.clientinfo.position['z']
        return {
            'x': x,
            'y': int(self.clientinfo.position['y']),
            'z': z
        }

    def get_block_coordinates(self, pos=None):
        if pos is None:
            pos = self.get_coordinates()
        return {
            'x': math.floor(pos['x']),
            'y': math.floor(pos['y']),
            'z': math.floor(pos['z'])
        }
