#coding: utf-8

"""""""""
定量的数値評価
Mean : 平均輝度の評価
Clarity : 画像の明瞭度の評価
CCI(Color Colorfulness Index) : 画像のカラフルさの評価
Entropy : 画像の情報量の評価
LOE(Lightness-Order-Error) : 自然度の保存を評価
GMSD(Gradient Magnitude Similarity Deviation) : 画像の勾配類似度の評価
"""""""""

import cv2
import numpy as np
from scipy import ndimage
from scipy import signal

#############################################################################
##                          画素値の総和                                   ##
#############################################################################
def Sum(img):
    H, W = img.shape[:2]
    sum = np.sum(img)
    mean = sum / (H * W)
    return mean

#############################################################################
##                          平均値(MEAN)                                   ##
#############################################################################
def Mean(img):
    H, W = img.shape[0], img.shape[1]
    b, g, r = cv2.split(img)
    Mean = (Sum(b) + Sum(g) + Sum(r)) / 3.0
    return Mean

#############################################################################
##                              Contrast                                   ##
#############################################################################
def Contrast(img):
    return (np.max(img) - np.min(img)) / (np.max(img) + np.min(img))

#############################################################################
##                         明瞭度(CLARIFY)                                 ##
#############################################################################
def Clarity(img, dst):
    sigmaImg = np.std(img)
    sigmaDst = np.std(dst)
    return np.log10(sigmaDst / (sigmaImg + sigmaDst)) - np.log10(1/2)

#############################################################################
##                   カラフルさ(COLOR COLORFULNESS INDEX)                  ##
#############################################################################
def CCI(img):
    b, g, r = cv2.split(img)
    rg = np.absolute(r - g)
    yb = np.absolute((r + g) / 2.0 - b)

    (rgMean, rgStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))

    stdRoot = np.sqrt((rgStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rgMean ** 2) + (ybMean ** 2))

    return stdRoot + (0.3 * meanRoot)

#############################################################################
##                              Entropy                                    ##
#############################################################################
def image_entropy(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    entropyValue = 0.0
    totalSize = img.shape[0] * img.shape[1]
    for i in range(0, 256):
        if(hist[i] > 0):
            entropyValue += (hist[i]/totalSize) * (np.log2(hist[i]/totalSize))
    return np.array(entropyValue) * (-1)

#############################################################################
##                        LOE(Lightness Order Error)                       ##
#############################################################################
def LOE(img, dst):
    H, W, n = img.shape
    b, g, r = cv2.split(img)
    db, dg, dr = cv2.split(dst)
    L = cv2.max(cv2.max(b, g), r)
    Le = cv2.max(cv2.max(db, dg), dr)

    r = 10.0 / np.min((H, W))
    Md = np.int(np.round((H * r)))
    Nd = np.int(np.round((W * r)))
    Ld = cv2.resize(L, (Nd, Md))
    Led = cv2.resize(Le, (Nd, Md))

    RD = np.zeros((Md, Nd))
    for y in range(0, Md):
        for x in range(0, Nd):
            E = np.zeros((Md, Nd))
            E = (Ld[y][x] >= Ld[:, :]) ^ (Led[y][x] >= Led[:, :])
            num = len(np.where(E == True)[0])
            RD[y][x] = num
    return np.sum(RD) / (Md * Nd)


#############################################################################
##                               GMSD                                      ##
#############################################################################
def GMSD(img, dst):
    H, W = img.shape
    c = 0.0026
    kernelX = np.array([[1, 0, -1],
                        [1, 0, -1],
                        [1, 0, -1]])
    kernelY = kernelX.T

    gi_x = cv2.filter2D(img, cv2.CV_32F, kernelX)
    gi_y = cv2.filter2D(img, cv2.CV_32F, kernelY)

    gr_x = cv2.filter2D(dst, cv2.CV_32F, kernelX)
    gr_y = cv2.filter2D(dst, cv2.CV_32F, kernelY)

    gi = np.sqrt(gi_x ** 2 + gi_y ** 2)
    gr = np.sqrt(gr_x ** 2 + gr_y ** 2)

    GMS = (2.0 * gi * gr + c) / (gi ** 2 + gr ** 2 + c)

    GMSM = np.mean(GMS)
    GMSD = np.sqrt(np.sum((GMS - GMSM) ** 2) / (H*W))
    return GMSD

if __name__ == '__main__':
    imgName = input('input image name : ')
    finName = input('Finish ImageName : ')
    fileName1 = input('file name 1: ')
    #fileName2 = input('file name 2: ')
    #fileName3 = input('file name 3: ')
    #fout = open("evaluate_data/evaluation.csv", "w")
    i = int(imgName)
    N = int(finName)
    print('----Start To Evaluate----')

    while (i <= N):
        img = cv2.imread("testdata/BMP/0" + str(i) + ".bmp" )
        result1 = cv2.imread("evaluate_data/" + fileName1 + "/0" + str(i) + ".bmp")
        #result2 = cv2.imread("evaluate_data/" + fileName2 + "/0" + str(i) + ".bmp")
        #result3 = cv2.imread("evaluate_data/" + fileName3 + "/0" + str(i) + ".bmp")
        print('----Input 0' + str(i) + '.bmp-----')
        #fout.writelines("----Evaluate 0" + str(i) + ".bmp-----\n")
        result_gray1 = cv2.cvtColor(result1, cv2.COLOR_BGR2GRAY)
        #result_gray2 = cv2.cvtColor(result2, cv2.COLOR_BGR2GRAY)
        #result_gray3 = cv2.cvtColor(result3, cv2.COLOR_BGR2GRAY)
        #img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        thresh = 22
        max_pixel = 255
        ret, img_dst = cv2.threshold(result_gray1,
                                     thresh,
                                     max_pixel,
                                     cv2.THRESH_BINARY)
        cv2.imwrite("evaluate_data/binary.bmp", img_dst)
        cv2.waitKey(0)
        #print('----Mean----')
        #print('Mean : ', Mean(result1))
        #fout.writelines("Mean\n")
        #fout.writelines(str(Mean(result1)) + "," + str(Mean(result2))+ "," + str(Mean(result3))+"\n")

        #print('----Clarify----')
        #print('Clarity : ', Clarity(img, result))
        #fout.writelines("Clarify\n")
        #fout.writelines(str(Clarity(img, result1)) + "," + str(Clarity(img, result2)) + "," + str(Clarity(img, result3)) + "\n")

        #print('----Color Colorfulness Index----')
        #print('CCI : ', CCI(result))
        #fout.writelines("CCI\n")
        #fout.writelines(str(CCI(result1))  + "," + str(CCI(result2)) + "," + str(CCI(result3))+  "\n")

        #print('----Entropy----')
        #print('Entropy : ', image_entropy(result_gray))
        #fout.writelines("Entropy\n")
        #fout.writelines(str(image_entropy(result_gray1)) + "," + str(image_entropy(result_gray2)) + "," + str(image_entropy(result_gray3)) + "\n")

        #print('----GMSD----')
        #print('GMSD : ', GMSD(img_gray, result_gray))
        #fout.writelines("GMSD\n")
        #fout.writelines(str(GMSD(img_gray, result_gray1)) + "," + str(GMSD(img_gray, result_gray2)) + "," + str(GMSD(img_gray, result_gray3)) + "\n")

        #print('----LOE----')
        #print('LOE : ', LOE(img, result))
        #fout.writelines("LOE\n")
        #fout.writelines(str(LOE(img, result1)) + "," + str(LOE(img, result2)) + "," + str(LOE(img, result3)) + "\n")

        i += 1
    print("---Program End----")