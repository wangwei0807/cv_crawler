import tempfile

import numpy as np
import cv2

from cv_crawler.captcha.lianzhong_api import get_coordinate, resolve


class ZhilianCaptcha(object):
    def __init__(self, raw=None):
        """
        :param raw: raw captcha image without any operation fetched from liepin.com
        """

        self.raw = None
        self.captcha = None
        if raw is not None:
            self.init_captcha(raw)

    def init_captcha(self, raw):
        """
        initial captcha with raw image
        :param raw: raw captcha image without any operation fetched from liepin.com
        :return:
        """
        self.raw = raw
        self.captcha = self.reformat_captcha(self.raw2cv(self.raw))

    @staticmethod
    def raw2cv(raw):
        """
        普通图片转换成cv2图片
        :param raw: normal image
        :return:
        """
        arr = np.asarray(bytearray(raw), dtype=np.uint8)
        return cv2.imdecode(arr, -1)

    @staticmethod
    def cv2raw(image):
        """
        convert cv2 image to image read from file
        :param image: cv2 image
        :return: normal image file
        """
        # with tempfile.NamedTemporaryFile(prefix='zhilian', suffix='.jpg') as tmp:
        #     cv2.imwrite(tmp.name, image)
        #     with open(tmp.name) as f:
        #         return f.read()
        cv2.imwrite('E://profiles//zhilian.jpg', image)
        with open('E://profiles//zhilian.jpg', 'rb') as f:
            return f.read()

    @staticmethod
    def split_image(cv2_image, nw, nh):
        slices = []
        height, width, dimen = cv2_image.shape
        print(height, width)
        ws = width // nw
        hs = height // nh
        for i in range(0, nh):
            for j in range(0, nw):
                slices.append(cv2_image[i * hs:(i + 1) * hs, j * ws:(j + 1) * ws, :])
        return slices

    @staticmethod
    def form_image(slices):
        w = 280
        h = 170
        seq = [10, 17, 14, 8, 1, 9, 4, 2, 3, 12, 19, 15, 11, 13, 6, 0, 5, 7, 16, 18, 35, 26, 37, 34, 22, 30, 29, 33, 23,
               27, 24, 31, 39, 32, 38, 21, 20, 36, 28, 25]
        idx_dict = [0] * len(seq)
        for i in range(0, len(seq)):
            idx_dict[seq[i]] = i
        img = np.zeros((h, w, 3), dtype=np.uint8)
        s = w // len(seq) * 2
        sh = h // 2
        c = len(seq) // 2
        for i in idx_dict:
            y = i % c
            x = i // c
            try:
                img[x * sh:(x + 1) * sh, y * s:(y + 1) * s, :] = slices[seq[i]]
            except ValueError:
                pass
        return img

    @staticmethod
    def reformat_captcha(image):
        """
        form image to right captcha from raw imag
        :param image: image in cv2 image type
        :return: captcha not mixed
        """
        slices = ZhilianCaptcha.split_image(image, 20, 2)
        out = ZhilianCaptcha.form_image(slices)
        return out

    def resolve(self, **kwargs):
        image = self.cv2raw(self.captcha)
        res = resolve(image=image)
        if not res:
            return []
        coordinates = []
        for coor in res.split('|'):
            c = coor.split(',')
            coordinates.append((int(c[0]), int(c[1])))
        return coordinates

    # def resolve(self, **kwargs):
    #     image = self.cv2raw(self.captcha)
    #     res = self.ocr.resolve(img=image, minlen='', maxlen='', _type=68)
    #     if not res:
    #         return []
    #     coordinates = []
    #     for coor in res.split('|'):
    #         c = coor.split(',')
    #         coordinates.append((int(c[0]), int(c[1])))
    #     return coordinates

    def mark_failed(self):
        pass

    def save(self, filename, **kwargs):
        cv2.imwrite(filename, self.captcha)
