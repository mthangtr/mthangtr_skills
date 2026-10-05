# identity_track.py - cosine similarity of the main face per sampled frame vs reference image(s)
# pip install insightface onnxruntime opencv-python numpy
# LICENSE: insightface code is MIT, but bundled pretrained models (buffalo_l) are NON-COMMERCIAL research only.
import sys, cv2, numpy as np
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l"); app.prepare(ctx_id=-1, det_size=(640, 640))  # ctx_id=-1 -> CPU
def emb(img):
    faces = app.get(img)
    if not faces: return None
    f = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))  # largest face
    return f.normed_embedding
ref = np.mean([emb(cv2.imread(p)) for p in sys.argv[2:]], axis=0); ref /= np.linalg.norm(ref)
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS) or 24; step = max(1, int(fps / 4)); i = 0
print("t,cos_sim")
while True:
    ok, fr = cap.read()
    if not ok: break
    if i % step == 0:
        e = emb(fr); print(f"{i/fps:.2f},{'' if e is None else round(float(np.dot(e, ref)), 3)}")
    i += 1
# usage: python identity_track.py take.mp4 ref_front.png ref_34.png > id.csv
