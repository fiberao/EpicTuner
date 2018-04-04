import numpy as np
import json, codecs, math
from PIL import Image, ImageDraw, ImageFont

prefix = "oko_resp_calc/output/mmdm15-37/"


def main(filename, get_x_y=True):
    resp = np.loadtxt(filename)
    i = 0
    # print(np.mean(resp))
    if get_x_y:
        min_val = np.min(resp)
        grid = (201, 201)
        resp_byte = np.zeros(grid, dtype=np.uint8)
        for x, y in np.nditer([resp, resp_byte], op_flags=['readwrite']):
            y[...] = int(x * 255.0 / min_val)

        resp_img = Image.fromarray(np.array(resp_byte, dtype=np.uint8), "L")
        resp_img.save(filename + ".jpg", "JPEG")
    resp_act_id = []
    posx_act_id = []
    posy_act_id = []
    for x in range(0, resp.shape[0],4):
        for y in range(0, resp.shape[1],4):
            x_real = x / 100.0 - 1.0
            y_real = y / 100.0 - 1.0
            if x_real * x_real + y_real * y_real < 1:
                i = i + 1
                if get_x_y:
                    resp_act_id.append(resp[x][y])
                else:
                    posx_act_id.append(x_real)
                    posy_act_id.append(y_real)
                    print(x,y)
                    print(i, x_real, y_real)
    print(i)
    if get_x_y:
        return resp_act_id
    else:
        return posx_act_id, posy_act_id


x_pos, y_pos = main(prefix + str(0).zfill(3) + ".txt", False)
json.dump(x_pos, codecs.open("wfx.txt", 'w', encoding='utf-8'),
          separators=(',', ':'), sort_keys=True, indent=4)
json.dump(y_pos, codecs.open("wfy.txt", 'w', encoding='utf-8'),
          separators=(',', ':'), sort_keys=True, indent=4)
ir = []
for each in range(1, 38):
    ir.append(main(prefix + str(each).zfill(3) + ".txt"))


json.dump(ir, codecs.open("ir.txt", 'w', encoding='utf-8'),
              separators=(',', ':'), sort_keys=True, indent=4)
