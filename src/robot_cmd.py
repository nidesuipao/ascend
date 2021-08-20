class UPComBotCommand(object):

    def start(self):
        password = [0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38, 0x38]
        buffer = self.GenerateCmd(0x0B, 0x0A, 0x71, 0x08, password)
        return buffer


    def Command(self, angle=0, speed=0, turn=0, time=500):
        data = [0] * 8
        data[0] = angle & 0xFF
        data[1] = (angle >> 8) & 0xFF
        data[2] = speed & 0xFF
        data[3] = (speed >> 8) & 0xFF
        data[4] = turn & 0xFF
        data[5] = (turn >> 8) & 0xFF
        data[6] = time & 0xFF
        data[7] = (time >> 8) & 0xFF
        buffer= self.GenerateCmd(0x0B, 0x08, 0x06, 0x08,data)
        return buffer

    def GenerateCmd(self,data_len, device_type, device_cmd, cmd_para_len, cmd_paras):
        buffer = [0] * (cmd_para_len + 9)
        buffer[0] = 0xFE
        buffer[1] = 0xEF
        buffer[2] = 0x00
        buffer[3] = 0x00
        # data_len
        buffer[4] = data_len & 0xFF
        check = buffer[4]
        buffer[5] = device_type & 0xFF
        check = check + buffer[5]
        buffer[6] = device_cmd & 0xFF
        check = check + buffer[6]
        buffer[7] = cmd_para_len & 0xFF
        check = check + buffer[7]
        for i in range(cmd_para_len):
            buffer[8 + i] = cmd_paras[i]
            check = check + buffer[8 + i]
        buffer[cmd_para_len + 8] = (~check) & 0xFF
        data_str = "".join(['{:08b}'.format(x) for x in buffer])
        cmd = bytearray([int(data_str[i:i + 8], 2) for i in range(0, len(data_str), 8)])
        return cmd

    def wave_hands(self):
        data = [0] * 1
        data[0] = 2 & 0xFF
        buffer= self.GenerateCmd(0x04,0x07, 0x55, 0x01, data)
        data_str = "".join(['{:08b}'.format(x) for x in buffer])
        cmd = bytearray([int(data_str[i:i + 8], 2) for i in range(0, len(data_str), 8)])
        return cmd

    def hit(self):
        data = [0] * 1
        data[0] = 4 & 0xFF
        buffer, length = self.GenerateCmd(0x04,0x07, 0x55, 0x01, data)
        data_str = "".join(['{:08b}'.format(x) for x in buffer])
        cmd = bytearray([int(data_str[i:i + 8], 2) for i in range(0, len(data_str), 8)])
        return cmd

    def call_action_by_name(self, name):
        length = len(name.encode())
        # data = name.encode()
        data = [0] * 5
        data[0] = 4 & 0xFF
        data[1] = 3000 & 0xFF
        data[2] = (3000 << 8) & 0xFF
        data[3] = 500 & 0xFF
        data[4] = (500 << 8) & 0xFF
        buffer, length = self.GenerateCmd(0x08,0x07, 0x5c, 0x05, data)
        data_str = "".join(['{:08b}'.format(x) for x in buffer])
        cmd = bytearray([int(data_str[i:i + 8], 2) for i in range(0, len(data_str), 8)])
        return cmd

    def check_operation(self, data):
        l = len(data)
        check = data[2]
        check = check + data[3]
        check = check + data[4]
        for i in range(data[4] - 1):
            check = check + data[5 + i]
        print("data calculated:", data[l - 1])
        if data[l - 1] == (~check) & 0xFF:
            print("OK")
            return True
        else:
            return False


if __name__ == '__main__':
    up = UPComBotCommand()
    up.wave_hands()
    up.call_action_by_name('hold')
