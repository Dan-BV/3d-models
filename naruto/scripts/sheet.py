from PIL import Image, ImageDraw, ImageFont
names=[('c1_medallion','1. Medallion'),('c2_headband','2. Headband plate'),('c3_spiral','3. Uzumaki spiral'),('c4_training','4. Training ground'),('c5_ichiraku','5. Ichiraku Ramen'),('c6_scroll','6. Jutsu scroll + clones'),('c7_gate','7. Konoha gate')]
W,H=450,500
sheet=Image.new('RGB',(W*4,H*2),'white')
f=ImageFont.truetype('arialbd.ttf',26)
for i,(n,t) in enumerate(names):
    im=Image.open(n+'.png').convert('RGB').resize((W,H))
    d=ImageDraw.Draw(im); d.rectangle([0,0,W,40],fill=(255,255,255)); d.text((12,6),t,fill=(30,30,30),font=f)
    sheet.paste(im,((i%4)*W,(i//4)*H))
sheet.save('concepts_sheet.png')
