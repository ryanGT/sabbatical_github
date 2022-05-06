import py_block_diagram
import importlib
importlib.reload(py_block_diagram)
#fn = "cart_pend_getting_ready_for_two_freqs/main.csv"
fn = "cart_pend_getting_ready_for_two_freqs/one_loop.csv"

myloader = py_block_diagram.csv_block_diagram_loader(fn)
myloader.main()
bd = myloader.block_diagram

#template_path = "two_freq_template.py"
template_path = "main_template.py"
out_folder = "cart_pend_getting_ready_for_two_freqs"
output_name= "main.py"
bd.generate_python_code(output_name, template_path, out_folder)

import shutil,os
src_path = os.path.join(out_folder, output_name)
dst_path = "main.py"
shutil.copyfile(src_path,dst_path)
