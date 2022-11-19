from os.path import join,isfile
from os import getcwd,remove,listdir

cwd = getcwd()
images_dir = join(cwd,"static","Images")
images_files = listdir(images_dir)
saved_image_face_data = join(cwd,"data.pkl")
saved_accounts = join(cwd,"accounts.pkl")

print("...Deteted Files...")
for image in images_files:
    print(image)
    remove(join(images_dir,image))

if isfile(saved_image_face_data):
    remove(saved_image_face_data)

if isfile(saved_accounts):
    remove(saved_accounts)

input("....Succesfully reseted....")