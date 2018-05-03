import cupy as np
import ast, json, codecs

prefix = "thorlabs"
with open(prefix + "/ir.txt", "r") as file:
    data = ast.literal_eval(file.read())
    ir = np.asarray(data)
with open(prefix + "/wfx.txt", "r") as file:
    data = ast.literal_eval(file.read())
    wfx = np.asarray(data)
with open(prefix + "/wfy.txt", "r") as file:
    data = ast.literal_eval(file.read())
    wfy = np.asarray(data)


# print(ir)
def calc_inv(ir):
    ir = np.transpose(ir)
    q = np.linalg.inv(np.matmul(np.transpose(ir), ir))
    hh = np.matmul(ir, np.transpose(q))
    print(hh)
    print(hh.shape)
    return hh.tolist()


json.dump({"resp": ir.tolist(), "wfx": wfx.tolist(),
           "wfy": wfy.tolist()}, codecs.open(prefix + "/" + prefix + ".json", 'w', encoding='utf-8'),
          separators=(',', ':'), sort_keys=True, indent=4)
json.dump({"inv": calc_inv(ir), "wfx": wfx.tolist(),
           "wfy": wfy.tolist()}, codecs.open(prefix + "/" + prefix + "_fit.json", 'w', encoding='utf-8'),
          separators=(',', ':'), sort_keys=True, indent=4)
