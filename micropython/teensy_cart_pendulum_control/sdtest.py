import uos
from machine import SDCard
sd = SDCard()
uos.mount(sd, '/sd')

sdpath = "/sd/test4.txt"
f = open(sdpath,'wb')
f.write("yet another test\n")
f.write("yup")
f.close()

uos.copy(sdpath,"/remote/")

uos.umount('/sd')
sd.deinit()
