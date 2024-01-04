import os
from os.path import join, dirname
from dotenv import load_dotenv

from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bson import ObjectId
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "SPARTA"

key_128bit = '2b7e151628aed2a6abf7158809cf4f3c'
# Fungsi untuk enkripsi teks menggunakan AES
def encrypt_text(key, plaintext):
    key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    return {
        'ciphertext': b64encode(ciphertext).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8'),
        'nonce': b64encode(nonce).decode('utf-8')
    }

def decrypt_text(key, encrypted_data):
    key = key.encode('utf-8')
    ciphertext = b64decode(encrypted_data['ciphertext'])
    tag = b64decode(encrypted_data['tag'])
    nonce = b64decode(encrypted_data['nonce'])
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_text = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_text.decode('utf-8')

# MONGODB_CONNECTION_STRING = "mongodb+srv://iqbalmp:iqbalmp@cluster0.ligsrx6.mongodb.net/?retryWrites=true&w=majority"
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]


@app.route("/")
def home():
    token_receive = request.cookies.get("mytoken")
    user = db.users.find()
    print(token_receive )
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        print(user_info)
        print(user)
        return render_template("index.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))



@app.route("/media_sosial")
def media_sosial():
    token_receive = request.cookies.get("mytoken")
    print(token_receive )
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template("index.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)


@app.route("/user/<username>")
def user(username):
    # endpoint untuk mengambil informasi profil user 
    # dan seluruh post mereka
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # jika ini profil saya, True
        # jika ini profil orang lain, False
        status = username == payload["id"]

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template("user.html", user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/chatting/<username>")
def chatting(username):
    # endpoint untuk mengambil informasi profil user 
    # dan seluruh post mereka
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # jika ini profil saya, True
        # jika ini profil orang lain, False
        status = username == payload["id"]

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template("chatting.html", user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    print(username_receive, pw_hash)
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )

    if result:
        payload = {
            "id": username_receive,
            # token ini hanya valid selama 24 jam
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    
    # Mari tangani kasus dimana kombinasi id dan 
        

    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    doc = {
        "username": username_receive,  # id
        "password": password_hash,  # password
        "profile_name": username_receive, 
         'role':'warga',
         'status':'false',
          # user's name is set to their id by default
        "profile_pic": "",  # profile image file name
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # a default profile image
        "profile_info": "",  # a profile description
    }
    db.users.insert_one(doc)
    return jsonify({"result": "success"})


@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    # ID kita harus memastikan apakah id telah digunakan
    username_receive = request.form["username_give"]
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route("/update_profile", methods=["POST"])
def save_img():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {"profile_name": name_receive, "profile_info": about_receive}
        if "file_give" in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/posting", methods=["POST"])
def posting():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # Kita membuat post baru di sini
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        decrypted_text = encrypt_text(key_128bit, comment_receive)
        print(decrypt_text)
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": decrypted_text,
            "date": date_receive,
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", "msg": "Posting successful!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/posting_chat", methods=["POST"])
def posting_chat():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # Kita membuat post baru di sini
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        username_tujuan = request.form["username"]
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "isi_chat": comment_receive,
            "date": date_receive,
            "username_tujuan": username_tujuan,
            
        }
        db.chats.insert_one(doc)
        return jsonify({"result": "success", "msg": "Posting successful!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route("/data_user", methods=["GET"])
def data_user():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        username_user=user_info['username']
        data_user = list(db.users.find({"username": {"$ne": username_user}}))
        print(data_user)
        for user in data_user:
            user["_id"] = str(user["_id"])
            
        return jsonify(
            {
                "result": "success",
                "msg": "Successful fetched all posts",
                "posts": data_user,
            })
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))
    
@app.route("/get_chat", methods=["GET"])
def get_chat():
    token_receive = request.cookies.get("mytoken")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.chats.find({}).sort("date", 1))
        else:
            posts = list(
                db.chats.find(
    {
        "$or": [
            {"username_tujuan": username_receive,"username":user_info["username"]},
            {"username_tujuan": user_info["username"],"username":username_receive}
        ]
    }
).sort("date", 1)
            )
        print(posts)

        for post in posts:
            if post["username"]==username_receive:
                post["jenis"]='kawan'
            else:
                post["jenis"]='sendiri'

            post["_id"] = str(post["_id"])
            
        return jsonify(
            {
                "result": "success",
                "msg": "Successful fetched all posts",
                "posts": posts,
            }
        )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=["GET"])
def get_posts():
    token_receive = request.cookies.get("mytoken")

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"username": payload["id"]})
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(
                db.posts.find(
    {
        "$or": [
            {"username": username_receive},
            {"username": user_info["username"]}
        ]
    }
).sort("date", -1)
            )
        

        for post in posts:
            post["isi_pesan"]=decrypt_text(key_128bit,post["comment"])
            if post["username"]==username_receive:
                post["jenis"]='kawan'
            else:
                post["jenis"]='sendiri'

            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "heart"}
            )
            post["heart_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "heart", "username": payload["id"]}
                )
            )

            post["count_star"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "star"}
            )
            post["star_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "star", "username": payload["id"]}
                )
            )

            post["count_like"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "like"}
            )
            post["like_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "like", "username": payload["id"]}
                )
            )
        return jsonify(
            {
                "result": "success",
                "msg": "Successful fetched all posts",
                "posts": posts,
            }
        )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/update_like", methods=["POST"])
def update_like():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # We should change the like count for the post here
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive,
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents(
            {"post_id": post_id_receive, "type": type_receive}
        )
        return jsonify({"result": "success", "msg": "updated", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/secret")
def secret():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        return render_template("secret.html")
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)