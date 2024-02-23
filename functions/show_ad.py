from utils.database import Database
from config import DB_NAME

db = Database(DB_NAME)

def next_ad(file_id,u_id):
    # print(u_id)
    file_ids = list(db.get_images_file_id(u_id))

    try:
        index = 0
        for i in file_ids:
            if file_id in i[0]:
                return file_ids[index+1][0]
            index +=1
    except:
        return None
def back_ad(file_id,u_id):
    # print(u_id)
    file_ids = list(db.get_images_file_id(u_id))
    index = 0
    for i in file_ids:
        if file_id in i[0]:
            if index-1 >= 0:
                # print(index)
                return file_ids[index-1][0]
            else:return None
        index +=1
def this_ad(file_id,u_id):
    file_ids = list(db.get_images_file_id(u_id))
    index = 0
    for i in file_ids:
        # print(i,file_id)
        if file_id in i[0]:
            return file_ids[index][0]
        index +=1
    # return "a"