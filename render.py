"""Build the original newspaper illustration; Pillow is needed only to rebuild.

The submitted Python program copies the resulting PNG using its standard library.
All drawing coordinates use the final 1024-pixel canvas, rendered at 3x for type.
"""
from pathlib import Path
from math import sin, cos, pi
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SCALE = 3
PAPER = '#F4F0E6'
INK = '#162C31'
MUTED = '#496064'
TEAL = '#156B70'
SEA = '#A8CED0'
PALE = '#D9E4DA'
RED = '#BD4B34'
GOLD = '#D8A74E'
WHITE = '#FFFCF5'
RULE = '#9EA8A0'

canvas = Image.new('RGB', (1024 * SCALE, 1024 * SCALE), PAPER)
d = ImageDraw.Draw(canvas)
FONT_DIR = Path('/usr/share/fonts')
FONTS = {
    'sans': FONT_DIR / 'truetype/liberation/LiberationSans-Regular.ttf',
    'bold': FONT_DIR / 'truetype/liberation/LiberationSans-Bold.ttf',
    'serif': FONT_DIR / 'opentype/urw-base35/NimbusRoman-Regular.otf',
    'title': FONT_DIR / 'opentype/urw-base35/NimbusRoman-Bold.otf',
    'italic': FONT_DIR / 'opentype/urw-base35/NimbusRoman-Italic.otf',
}


def font(size, style='sans'):
    return ImageFont.truetype(str(FONTS[style]), round(size * SCALE))


def box(bounds, fill, outline=None, width=1, radius=0):
    coords = tuple(round(v * SCALE) for v in bounds)
    if radius:
        d.rounded_rectangle(coords, radius=round(radius * SCALE), fill=fill,
                            outline=outline, width=max(1, round(width * SCALE)))
    else:
        d.rectangle(coords, fill=fill, outline=outline,
                    width=max(1, round(width * SCALE)))


def line(points, fill=INK, width=1):
    d.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
           fill=fill, width=max(1, round(width * SCALE)), joint='curve')


def poly(points, fill, outline=None, width=1):
    points = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
    d.polygon(points, fill=fill)
    if outline:
        d.line(points + [points[0]], fill=outline,
               width=max(1, round(width * SCALE)), joint='curve')


def ellipse(bounds, fill=None, outline=None, width=1):
    d.ellipse(tuple(round(v * SCALE) for v in bounds), fill=fill,
              outline=outline, width=max(1, round(width * SCALE)))


def text(x, y, value, size=20, style='sans', color=INK):
    d.text((round(x * SCALE), round(y * SCALE)), value,
           font=font(size, style), fill=color, anchor='lt')


def width(value, size, style='sans'):
    return d.textlength(value, font=font(size, style)) / SCALE


def centered(cx, y, value, size=20, style='sans', color=INK):
    text(cx - width(value, size, style) / 2, y, value, size, style, color)


def paragraph(x, y, value, max_width, size=19, leading=23, color=INK):
    words = value.split()
    current = ''
    for word in words:
        candidate = (current + ' ' + word).strip()
        if width(candidate, size) > max_width and current:
            text(x, y, current, size, color=color)
            y += leading
            current = word
        else:
            current = candidate
    if current:
        text(x, y, current, size, color=color)
        y += leading
    return y


def category(x, y, value, color=TEAL):
    text(x, y, value, 13, 'bold', color)


def sun(cx, cy, r, color=GOLD):
    ellipse((cx-r, cy-r, cx+r, cy+r), color)


def wave(x, y, w, color=TEAL, amplitude=3, period=35, weight=1):
    line([(x+i, y+sin(i / period * 2*pi)*amplitude)
          for i in range(0, int(w)+1, 2)], color, weight)


def star(cx, cy, r, color):
    poly([(cx+cos(-pi/2+i*pi/5)*(r if i%2==0 else r*.4),
           cy+sin(-pi/2+i*pi/5)*(r if i%2==0 else r*.4))
          for i in range(10)], color)


def plane(cx, cy, scale=1, color=INK):
    pts=[(-35,0),(-7,-7),(-3,-24),(4,-24),(9,-6),(35,1),
         (35,5),(9,4),(5,20),(-2,20),(-6,4),(-35,4)]
    poly([(cx+x*scale, cy+y*scale) for x,y in pts], color)


def bridge_scene(x, y, w, h):
    box((x,y,x+w,y+h), '#DDE6DE')
    sun(x+w-85,y+37,26)
    for i in range(6):
        line([(x+16,y+15+i*7),(x+160-i*14,y+15+i*7)], '#B3C8C2', .7)
    poly([(x,y+97),(x+45,y+72),(x+105,y+93),(x+170,y+86),
          (x+215,y+109),(x+w,y+108),(x+w,y+h),(x,y+h)], SEA)
    # The parallel rail crossing remains drawn in the background.
    line([(x+14,y+83),(x+w-14,y+78)], '#5C7476', 4)
    for xx in range(28, int(w)-10, 44):
        line([(x+xx,y+82),(x+xx,y+105)], '#5C7476', 2)
    # Road arch with its central section fallen; a schematic, no photograph.
    for a,b in [(12,240),(383,w-12)]:
        poly([(x+a,y+110),(x+b,y+105),(x+b,y+115),(x+a,y+121)], INK)
        line([(x+a,y+108),(x+b,y+103)], WHITE, 1.4)
        for xx in range(a+25,int(b),50):
            poly([(x+xx,y+119),(x+xx+8,y+117),
                  (x+xx+7,y+149),(x+xx-1,y+149)], '#526969')
    poly([(x+239,y+110),(x+255,y+118),(x+269,y+130),
          (x+262,y+142),(x+244,y+132)], '#647778', INK)
    poly([(x+287,y+142),(x+329,y+151),(x+358,y+138),
          (x+369,y+148),(x+334,y+160),(x+287,y+151)], '#7C8D8C', INK)
    line([(x+281,y+145),(x+295,y+117),(x+320,y+129),
          (x+348,y+148)], INK, 4)
    for xx in [290,302,315,329,341]:
        line([(x+xx,y+131),(x+xx+6,y+149)], INK, 1)
    line([(x+211,y+109),(x+223,y+102),(x+231,y+109)], RED, 3)
    line([(x+384,y+108),(x+393,y+102),(x+402,y+106)], RED, 3)
    for yy in [155,168,181]:
        wave(x+12,y+yy,w-24,TEAL,1.7,45,.7)
    box((x+14,y+139,x+158,y+162), WHITE)
    text(x+22,y+144,'KERCH STRAIT',12,'bold',TEAL)
    box((x+w-152,y+154,x+w-14,y+177), WHITE)
    text(x+w-144,y+159,'ROAD SPAN HIT',12,'bold',RED)


def gulf_scene(x,y,w,h):
    box((x,y,x+w,y+h), '#E9DDC4')
    sun(x+w-41,y+32,20)
    poly([(x,y+h-31),(x+40,y+h-47),(x+95,y+h-31),
          (x+w,y+h-38),(x+w,y+h),(x,y+h)], '#C2B99D')
    # The radar stays intact, since Bahrain/US report interception.
    poly([(x+73,y+h-18),(x+96,y+h-18),(x+85,y+57)], INK)
    ellipse((x+63,y+42,x+107,y+70), None, INK, 3)
    line([(x+67,y+48),(x+104,y+64)], INK, 2)
    line([(x+85,y+45),(x+88,y+28)], INK, 2)
    for i in range(3):
        # Radio arcs rise towards the incoming drone.
        d.arc(tuple(round(v*SCALE) for v in
                    (x+83+i*11,y+16-i*9,x+132+i*19,y+69+i*8)),
              220,305,fill=TEAL,width=2*SCALE)
    plane(x+207,y+26,.47)
    line([(x+135,y+91),(x+168,y+52)], WHITE,3)
    line([(x+169,y+43),(x+173,y+34)], RED,2)
    line([(x+162,y+37),(x+154,y+31)], RED,2)
    line([(x+178,y+43),(x+186,y+44)], RED,2)
    box((x+10,y+h-22,x+w-10,y+h-3),WHITE)
    text(x+17,y+h-19,'BAHRAIN SAYS: INTERCEPTED',10.5,'bold',TEAL)


def globe(cx,cy,r):
    ellipse((cx-r,cy-r,cx+r,cy+r),SEA,INK,1.6)
    ellipse((cx-r*.5,cy-r,cx+r*.5,cy+r),None,TEAL,.7)
    line([(cx-r,cy),(cx+r,cy)],TEAL,.7)
    for yy in [-.45,.45]:
        line([(cx-r*.87,cy+r*yy),(cx+r*.87,cy+r*yy)],TEAL,.7)
    land=[(-.55,-.65),(-.12,-.63),(.04,-.38),(-.14,-.12),
          (.06,.06),(-.03,.45),(-.22,.76),(-.35,.33),
          (-.51,.1),(-.37,-.19),(-.71,-.31)]
    poly([(cx+a*r,cy+b*r) for a,b in land],TEAL)
    poly([(cx+r*.28,cy-r*.54),(cx+r*.71,cy-r*.37),
          (cx+r*.64,cy-r*.06),(cx+r*.25,cy+r*.06)],TEAL)


def cop_scene(x,y,w,h):
    box((x,y,x+w,y+h),PALE)
    globe(x+68,y+45,32)
    box((x+137,y+21,x+213,y+71),WHITE,INK,1)
    text(x+148,y+30,'COP31',19,'bold',TEAL)
    for yy in [56,61]:line([(x+148,y+yy),(x+199,y+yy)],RULE,1)
    # A negotiation table and three anonymous delegates, not named portraits.
    for xx in [119,160,200,239]:
        ellipse((x+xx-5,y+9,x+xx+5,y+19),INK)
    line([(x+114,y+76),(x+245,y+76)],INK,3)
    line([(x+122,y+78),(x+117,y+89)],INK,2)
    line([(x+237,y+78),(x+241,y+89)],INK,2)


def sudan_scene(x,y,w,h):
    box((x,y,x+w,y+h),'#EBDDD0')
    # Families and a shelter: no graphic depiction of violence.
    poly([(x+12,y+75),(x+43,y+40),(x+76,y+75)],'#C4A48A',INK,1)
    box((x+38,y+59,x+50,y+75),PAPER)
    for xx,hh in [(87,20),(105,29),(124,18)]:
        ellipse((x+xx-4,y+55-hh,x+xx+4,y+63-hh),INK)
        line([(x+xx,y+64-hh),(x+xx,y+73)],INK,4)
    plane(x+88,y+20,.33,RED)
    text(x+151,y+13,'1,630+',36,'title',RED)
    text(x+154,y+53,'killed by drones',15,'bold')
    text(x+154,y+72,'JAN–OCT · UN VERIFIED',10,'bold',MUTED)


def flag(x,y,w,h,nation):
    if nation=='US':
        box((x,y,x+w,y+h),WHITE)
        for i in range(0,7):
            box((x,y+i*h/7,x+w,y+i*h/7+h/14),RED)
        box((x,y,x+w*.45,y+h*.52),INK)
        for a in range(3):
            for b in range(2):sun(x+5+a*5,y+4+b*5,1,WHITE)
    elif nation=='IN':
        box((x,y,x+w,y+h/3),GOLD)
        box((x,y+h/3,x+w,y+2*h/3),WHITE)
        box((x,y+2*h/3,x+w,y+h),TEAL)
        ellipse((x+w/2-3,y+h/2-3,x+w/2+3,y+h/2+3),None,INK,.8)
    elif nation=='JP':
        box((x,y,x+w,y+h),WHITE)
        sun(x+w/2,y+h/2,h*.25,RED)
    elif nation=='AU':
        box((x,y,x+w,y+h),INK)
        line([(x+2,y+2),(x+w*.42,y+h*.46)],WHITE,3)
        line([(x+2,y+h*.46),(x+w*.42,y+2)],WHITE,3)
        line([(x+w*.22,y+1),(x+w*.22,y+h*.48)],RED,2)
        line([(x+1,y+h*.23),(x+w*.44,y+h*.23)],RED,2)
        for xx,yy in [(.68,.25),(.77,.57),(.55,.75),(.87,.77)]:
            star(x+w*xx,y+h*yy,2.2,WHITE)
    line([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],INK,.6)


def quad_scene(x,y,w,h):
    box((x,y,x+w,y+h),'#D6E4E0')
    for i,country in enumerate(['US','AU','IN','JP']):
        xx=x+25+i*65
        flag(xx,y+9,39,24,country)
        centered(xx+19.5,y+40,country,11,'bold')
    for yy in [64,77,88]:wave(x+13,y+yy,w-26,TEAL,1.7,38,.8)
    line([(x+20,y+65),(x+61,y+77),(x+107,y+63),
          (x+155,y+77),(x+206,y+68),(x+275,y+81)],INK,2.5)
    for xx,yy in [(61,77),(155,77),(275,81)]:
        ellipse((x+xx-3,y+yy-3,x+xx+3,y+yy+3),GOLD,INK,.8)


def chip_scene(x,y,w,h):
    box((x,y,x+w,y+h),'#DDE2CB')
    box((x+16,y+18,x+89,y+78),INK,radius=4)
    box((x+30,y+30,x+76,y+65),TEAL,WHITE,.7)
    text(x+38,y+40,'AI',22,'bold',WHITE)
    for yy in range(25,78,9):
        line([(x+8,y+yy),(x+15,y+yy)],INK,2)
        line([(x+90,y+yy),(x+99,y+yy)],INK,2)
    for xx in range(23,89,10):
        line([(x+xx,y+9),(x+xx,y+17)],INK,2)
        line([(x+xx,y+79),(x+xx,y+87)],INK,2)
    text(x+116,y+11,'$115.8bn',34,'title',TEAL)
    text(x+119,y+54,'Q3 REVENUE',13,'bold')
    text(x+119,y+73,'+103% YEAR ON YEAR',11,'bold',MUTED)


def trade_scene(x,y,w,h):
    box((x,y,x+w,y+h),'#E8D8CB')
    # Maple leaf and a Chinese flag above a cargo ship.
    box((x+17,y+11,x+73,y+41),WHITE)
    box((x+17,y+11,x+29,y+41),RED)
    box((x+61,y+11,x+73,y+41),RED)
    leaf=[(0,-12),(3,-5),(8,-7),(6,-2),(13,1),(8,5),
          (9,9),(2,8),(1,14),(-1,14),(-2,8),(-9,9),
          (-8,5),(-13,1),(-6,-2),(-8,-7),(-3,-5)]
    poly([(x+45+a*.7,y+25+b*.7) for a,b in leaf],RED)
    box((x+226,y+11,x+282,y+41),RED)
    star(x+240,y+21,6,GOLD)
    line([(x+90,y+25),(x+207,y+25)],TEAL,2)
    poly([(x+90,y+25),(x+99,y+20),(x+99,y+30)],TEAL)
    poly([(x+207,y+25),(x+198,y+20),(x+198,y+30)],TEAL)
    for i,color in enumerate([TEAL,GOLD,RED]):
        box((x+98+i*25,y+52,x+121+i*25,y+66),color,INK,.6)
    box((x+184,y+45,x+198,y+68),WHITE,INK,.8)
    poly([(x+71,y+67),(x+222,y+67),(x+204,y+85),(x+90,y+85)],INK)
    wave(x+14,y+91,w-28,TEAL,1.5,32,.8)


def forest_scene(x,y,w,h):
    box((x,y,x+w,y+h),'#D8E2C9')
    for cx,cy,r in [(28,37,25),(61,24,26),(90,43,29),
                    (126,24,23),(154,45,27),(189,24,25)]:
        line([(x+cx,y+cy),(x+cx,y+83)],'#6C7753',4)
        ellipse((x+cx-r,y+cy-r,x+cx+r,y+cy+r),TEAL)
        for i in [-.4,.2]:
            line([(x+cx-r*.5,y+cy+r*i),(x+cx+r*.5,y+cy+r*i)],'#56908A',.7)
    box((x+212,y+69,x+w,y+h),'#C8AD80')
    for xx in [222,244,270]:
        box((x+xx,y+65,x+xx+10,y+81),'#8D6D4F')
        ellipse((x+xx,y+62,x+xx+10,y+68),PAPER,INK,.6)
    line([(x+205,y+11),(x+205,y+90)],RED,2)
    box((x+10,y+72,x+154,y+91),WHITE)
    text(x+17,y+76,'AWÁ · BRAZIL',11,'bold',TEAL)


# One typographic system and aligned newspaper columns.
box((20,20,1004,1004),None,INK,1)
category(34,32,'THE WORLD, IN ONE DAY')
text(34,53,'WORLD DAILY',65,'title')
text(687,46,'TUESDAY',16,'bold',MUTED)
text(686,70,'17 NOVEMBER',31,'bold')
text(900,108,'2026',25,'title',TEAL)
text(34,123,'Conflict · diplomacy · climate · people · technology',17,'italic',MUTED)
line([(34,148),(990,148)],INK,3)

category(34,162,'01 / EUROPE · UKRAINE & RUSSIA',RED)
text(34,184,'Ukraine hits',48,'title')
text(34,232,'Kerch bridge again',48,'title')
bridge_scene(34,286,622,193)
paragraph(34,491,'Ukraine hits Kerch’s road span again; Russia targets Kyiv’s bridges and infrastructure.',622,21,25)

line([(676,162),(676,550)],RULE,.8)
category(694,162,'02 / MIDDLE EAST',RED)
text(694,186,'Iran & US',35,'title')
text(694,224,'exchange fire',35,'title')
gulf_scene(694,278,296,141)
paragraph(694,433,'Bahrain and US say Iranian drones aimed at a US radar were intercepted. US says it struck an Iranian launch site.',294,19,23)

line([(34,563),(990,563)],INK,1.5)
colx=[34,362,690]
for xx in [348,676]:line([(xx,577),(xx,992)],RULE,.8)
category(34,578,'03 / CLIMATE · TÜRKIYE')
category(362,578,'04 / AFRICA · SUDAN',RED)
category(690,578,'05 / INDO-PACIFIC · MANILA')
cop_scene(34,601,300,92)
sudan_scene(362,601,300,92)
quad_scene(690,601,300,92)
text(34,708,'COP31: draft disputed',27,'title')
paragraph(34,740,'Ministers negotiate finance and fossil fuels; EU pushes back on the draft deal.',300,18.5,22)
text(362,708,'Sudan: UN reports toll',27,'title')
paragraph(362,740,'New report documents 2,230+ civilian deaths in Jan–Oct; most were drone victims.',300,18.5,22)
text(690,708,'Quad summit in Manila',27,'title')
paragraph(690,740,'US, Australia, India and Japan announce maritime, AI and cable cooperation.',300,18.5,22)

line([(34,815),(990,815)],INK,1)
category(34,829,'06 / BUSINESS · UNITED STATES')
category(362,829,'07 / TRADE · CANADA & CHINA')
category(690,829,'08 / AMAZON · BRAZIL')
chip_scene(34,851,300,96)
trade_scene(362,851,300,96)
forest_scene(690,851,300,96)
text(34,958,'Nvidia sales double',25,'title')
text(362,958,'Tariff relief expands',25,'title')
text(690,958,'Awá footage raises alarm',24,'title')
text(34,986,'Quarterly results released',17,'sans',MUTED)
text(362,986,'Xi & Carney agree in Shenzhen',17,'sans',MUTED)
text(690,986,'Advocates warn of forest threats',17,'sans',MUTED)

canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(ROOT/'entry.png', optimize=True)
print('Rendered', ROOT/'entry.png')
