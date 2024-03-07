# Imports
from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import zipfile
import shutil
from pathlib import Path
import glob
import moviepy.editor as moviepy
import sys
import torch

# Import Demos
import demo
import demo_flow

# !!Using Flask and CORS!!
app = Flask(__name__)
CORS(app)

# Configuration folders
# If you need to change folder you must keep the format of how the folder are written
app.config['zip_folder'] = './zips/'
app.config['upload_folder'] = './imported/'
app.config['thumb_folder'] = './thumbnails/'
app.config['computed_folder'] = './precomputed/'


# Useful Methods
def delete_content_folder(folder_path):
    folder = folder_path
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


# def rename_as_pred(folder_path, video_type='rgb'):
#     folder = folder_path
#     for the_file in os.listdir(folder):
#         file_path = os.path.join(folder, the_file)
#         print(file_path)
#         try:
#             if os.path.isfile(file_path):
#                 if "out_" in the_file and ".avi" in the_file:
#                     outfile = os.path.join(folder, str(video_type) + '_' + the_file[4:])
#                     os.rename(file_path, outfile)
#                     os.remove(outfile)
#                 elif "out_" not in file_path:
#                     os.remove(file_path)
#         except Exception as e:
#             print(e)


def generate_thumbs(folder):
    thumbs_folder = os.path.join(app.config['thumb_folder'], folder.split('/')[-1])
    try:
        os.mkdir(thumbs_folder)
        for infile in glob.glob(os.path.join(folder, '*')):
            if "T_" not in infile and "out_" in infile:
                print('im here')
                print(infile)
                clip = moviepy.VideoFileClip(infile)
                clip.write_videofile(os.path.join(thumbs_folder, "T_" + infile.split('/')[-1][4:-3] + "mp4"),
                                     codec='libx264')
    except Exception as e:
        print(e)



def zipdir(foldername):
    try:
        shutil.make_archive(os.path.join(app.config['zip_folder'], foldername), 'zip', os.path.join(app.config['upload_folder'], foldername))
    except Exception as e:
        print(e)


def unzip(filezip):
    try:
        zip_ref = zipfile.ZipFile(filezip, 'r')
        zip_ref.extractall(app.config['thumb_folder'])
        zip_ref.close()
        #shutil.unpack_archive(os.path.join(app.config['upload_folder'], foldername), 'zip', os.path.join(app.config['upload_folder'], foldername))
    except Exception as e:
        print(e)


def check_video(foldername, model_path, video_type='rgb'):
    assert video_type in ['rgb', 'flow']
    foldername = str(foldername).strip()
    # These are the mimetype available, if you want to add a new one feel free to do it! (Check if the demo can handle it)
    mime = ['video/mp4', 'video/avi']
    # Check if the name is empty
    if not foldername == "":
        # Replace all spaces w/ underscores
        foldername = str(foldername).replace(' ', '_')
        if not os.path.isdir(os.path.dirname(app.config['upload_folder'] + foldername + '/')):
            os.makedirs(os.path.dirname(app.config['upload_folder'] + foldername + '/'))
            videos = request.files.getlist('videos[]')
            if len(videos) > 50:
                return json.dumps({"message": 'The maximum number of image that you can upload is 50'})
            print(videos, file=sys.stderr)
            for video in videos:
                mimetype = video.content_type
                if mimetype in mime:
                    filename = secure_filename(video.filename)
                    video.save(os.path.join(app.config['upload_folder'] + foldername, filename))

            print("Running pretrained, please wait", file=sys.stderr)
            for video in os.listdir(os.path.join(app.config['upload_folder'], foldername)):
                if video_type == 'rgb':
                    demo.test_full_image_network(
                        video_path=os.path.join(app.config['upload_folder'], foldername, video),
                        model_path=model_path,
                        output_path=os.path.join(app.config['upload_folder'], foldername), cuda=torch.cuda.is_available())
                elif video_type == 'flow' and 'flow' in video:
                    print(video)
                    demo_flow.test_full_image_network(
                        video_path=os.path.join(app.config['upload_folder'], foldername, video),
                        model_path=model_path,
                        output_path=os.path.join(app.config['upload_folder'], foldername), cuda=torch.cuda.is_available())
            print("Inference completed!", file=sys.stderr)

            generate_thumbs(os.path.join(app.config['upload_folder'], foldername))
            #rename_as_pred(os.path.join(app.config['upload_folder'], foldername), video_type)
            zipdir(foldername)
            delete_content_folder(app.config['upload_folder'])
            print("Concluding", file=sys.stderr)

            return json.dumps({"message": 'Done'})
        return json.dumps({"message": 'Unable to upload with this name'})
    return json.dumps({"message": 'Insert a valid name'})


@app.route('/upload-optical_flow', methods=['POST'])
def upload_flow():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/flow/flow_c23_all_ff.tar', video_type='flow')


@app.route('/upload-deepfake', methods=['POST'])
def upload_deepfake():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/flow/flow_c23_Deepfakes_ff.tar', video_type='flow')


@app.route('/upload-face2face', methods=['POST'])
def upload_face2face():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/flow/flow_c23_Face2Face_ff.tar', video_type='flow')


@app.route('/upload-faceswap', methods=['POST'])
def upload_faceswap():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/flow/flow_c23_FaceSwap_ff.tar', video_type='flow')


@app.route('/upload-neuraltextures', methods=['POST'])
def upload_neuraltextures():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/flow/flow_c23_NeuralTextures_ff.tar', video_type='flow')


@app.route('/upload-rgb', methods=['POST'])
def upload_rgb():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/rgb/rgb_c23_all_ff.tar')


@app.route('/upload-deepfake_rgb', methods=['POST'])
def upload_deepfake_rgb():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/rgb/rgb_c23_Deepfakes_ff.tar')


@app.route('/upload-face2face_rgb', methods=['POST'])
def upload_face2face_rgb():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/rgb/rgb_c23_Face2Face_ff.tar')


@app.route('/upload-faceswap_rgb', methods=['POST'])
def upload_faceswap_rgb():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/rgb/rgb_c23_FaceSwap_ff.tar')


@app.route('/upload-neuraltextures_rgb', methods=['POST'])
def upload_neuraltextures_rgb():
    foldername = request.form.get('name')
    return check_video(foldername, model_path='pretrained/rgb/rgb_c23_NeuralTextures_ff.tar')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/videos')
def pre_computed():
    return render_template("videos.html")


# DONE
@app.route('/check', methods=['GET'])
def check():
    files = {}
    path = app.config['zip_folder']
    sorted_paths = [str(p).split('zips/')[-1] for p in sorted(Path(path).iterdir(), key=os.path.getmtime, reverse=True)]
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            dim = os.stat(path + f).st_size
            files[f] = dim

    zips = [[z, files[z]] for z in sorted_paths if z in files]
    return json.dumps(zips)


# DONE
@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('name', default='none.zip')
    path = os.path.join(app.config['zip_folder'], filename)
    pathA = Path(path)
    if pathA.exists():
        return send_file(path, as_attachment=True)

    return json.dumps({"message": "File doesnt exist"})


# DONE
@app.route('/getList', methods=['GET'])
def get_list():
    filename = request.args.get('name', default='none.zip')
    foldername = filename.split('.zip')[0]
    path = app.config['thumb_folder']

    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        if dirpath == os.path.join(path, foldername):
            for f in filenames:
                if os.path.isfile(os.path.join(dirpath, f)) and 'mp4' in f:
                    out_file = os.path.join(dirpath, f)[2:]
                    files.append(out_file)
    return json.dumps(files)


@app.route('/getPreComputed', methods=['GET'])
def get_computed():
    path = app.config['computed_folder']
    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            if os.path.isfile(os.path.join(dirpath, f)) and 'mp4' in f:
                out_file = os.path.join(dirpath, f)[2:]
                files.append(out_file)
    files = sorted(files)

    return json.dumps(files)


# DONE
@app.route('/thumb', methods=['GET'])
def thumb():
    thumb = str(request.args.get('name', default=""))

    return send_file(thumb, mimetype="video")


# DONE
@app.route('/delete', methods=['GET'])
def delete():
    filename = request.args.get('name', default='none.zip')
    foldername = filename.split('.zip')[0]
    path = os.path.join(app.config['zip_folder'], filename)
    pathA = Path(path)
    if pathA.exists():
        os.remove(path)
        if Path(os.path.join(app.config['thumb_folder'], foldername)).exists():
            if os.path.isdir(Path(os.path.join(app.config['thumb_folder'], foldername))):
                shutil.rmtree(Path(os.path.join(app.config['thumb_folder'], foldername)))
            else:
                os.remove(Path(os.path.join(app.config['thumb_folder'], foldername)))
        if Path(os.path.join(app.config['upload_folder'], foldername)).exists():
            if os.path.isdir(Path(os.path.join(app.config['upload_folder'], foldername))):
                shutil.rmtree(Path(os.path.join(app.config['upload_folder'], foldername)))
            else:
                os.remove(Path(os.path.join(app.config['upload_folder'], foldername)))
        return json.dumps({"message": "Done"})

    return json.dumps({"message": "File doesnt exsist!"})


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=80, threaded=True)
    app.run(debug=True)
