import sys
import os, shutil
import json

def main(input_dir, output_dir):
    f_list = os.listdir(output_dir)
    for label in os.listdir(input_dir):
        if os.path.splitext(label)[1] == '.json':
            in_label = os.path.join(input_dir, label)
            out_label = os.path.join(output_dir, label)
            if label in f_list:
                data_out = json.load(open(out_label))
                data_in = json.load(open(in_label))
                data_out['shapes'] = data_out['shapes'] + data_in['shapes']
                with open(out_label,"w") as f:
                    json.dump(data_out, f, ensure_ascii=False, indent=2)
            else:
                shutil.copyfile(in_label, out_label)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("Error: [usage] python combine.py INPUT1 INPUT2")
        print ("INPUT1 will be combine into INPUT2")
        exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    if not os.path.isdir(input_dir):
        print ("Error: No directory named {}.".format(input_dir))
        exit(1)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    main(input_dir, output_dir)
