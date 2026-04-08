import numpy as np
import socket
from skimage.measure import label

host = "84.237.21.36"
port = 5152

def recvall(sock, nbytes):
    data = bytearray()
    while len(data) < nbytes:
        packet = sock.recv(nbytes - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def distance(px1, px2):
    return ((px1[0]-px2[0])**2 + (px1[1]-px2[1])**2)**0.5

def find_two_centroids(img):
    for threshold in [200, 180, 150, 120, 100, 80]:
        labeled = label(img > threshold)
        unique_labels = np.unique(labeled[labeled > 0])
        
        if len(unique_labels) >= 2:
            areas = [(np.sum(labeled == lbl), lbl) for lbl in unique_labels]
            areas.sort(reverse=True)

            y1, x1 = np.where(labeled == areas[0][1])
            y2, x2 = np.where(labeled == areas[1][1])
            
            c1 = (np.mean(y1), np.mean(x1))
            c2 = (np.mean(y2), np.mean(x2))
            return c1, c2
    

    flat = img.flatten()
    idx1 = np.argmax(flat)
    flat[idx1] = 0
    idx2 = np.argmax(flat)
    y1, x1 = divmod(idx1, img.shape[1])
    y2, x2 = divmod(idx2, img.shape[1])
    return (y1, x1), (y2, x2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    for i in range(10):
        sock.send(b"get")
        bts = recvall(sock, 40002)
        img = np.frombuffer(bts[2:], dtype="uint8").reshape(bts[0], bts[1])
        
        c1, c2 = find_two_centroids(img)
        dist = round(distance(c1, c2), 1)
        
        sock.send(f"{dist:.1f}".encode())
        response = sock.recv(10)
        print(f"{i+1}: distance={dist}, server={response}")
        
        if i < 9:
            sock.send(b"beat")
            sock.recv(10)