import PIL.Image as Image
import qrcode
import sys

sticker = Image.open("mockup.png")
offset = (41, 406)

n = int( sys.argv[1])
for i in xrange(n):
    qr = qrcode.QRCode(
        border=0,
    )
    qr.add_data('http://se.cretfi.re/gear/{i}'.format(i=i))
    qr_img = qr.make_image()
    qr_img.thumbnail((210,210))
    sticker.paste(qr_img, offset)

    sticker.save("output/{i:03d}.png".format(i=i))
