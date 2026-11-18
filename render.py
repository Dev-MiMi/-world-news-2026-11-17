"""Build the original newspaper illustration; Pillow is needed only to rebuild.

The submitted Python program copies the resulting PNG using its standard library.
All drawing coordinates use the final 1024-pixel canvas, rendered at 3x for type.
"""
from pathlib import Path
from math import sin, cos, pi
import argparse
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


def paragraph(x, y, value, max_width, size=19, leading=23, color=INK,
              style='sans'):
    words = value.split()
    current = ''
    for word in words:
        candidate = (current + ' ' + word).strip()
        if width(candidate, size, style) > max_width and current:
            text(x, y, current, size, style, color)
            y += leading
            current = word
        else:
            current = candidate
    if current:
        text(x, y, current, size, style, color)
        y += leading
    return y


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


def illustration(scene,x,y,w,h,native_w=300,native_h=92):
    """Render one original diagram separately to keep panels inside their bounds."""
    global canvas,d
    page,page_draw=canvas,d
    canvas=Image.new('RGB',(native_w*SCALE,native_h*SCALE),PAPER)
    d=ImageDraw.Draw(canvas)
    scene(0,0,native_w,native_h)
    # Preserve circles, flags and lettering when fitting the short picture strip.
    factor=min(w/native_w,h/native_h)
    tile=canvas.resize((round(native_w*factor*SCALE),
                        round(native_h*factor*SCALE)),Image.Resampling.LANCZOS)
    strip=Image.new('RGB',(round(w*SCALE),round(h*SCALE)),canvas.getpixel((0,0)))
    strip.paste(tile,((strip.width-tile.width)//2,(strip.height-tile.height)//2))
    canvas,d=page,page_draw
    canvas.paste(strip,(round(x*SCALE),round(y*SCALE)))


def lead_scene(x,y,w,h):
    """Road and rail are separate in this schematic of the Kerch crossing."""
    box((x,y,x+w,y+h),'#DDE6DE')
    box((x,y+h*.38,x+w,y+h),SEA)
    sun(x+w-42,y+22,15)
    for i in range(4):
        line([(x+14,y+13+i*5),(x+170-i*24,y+13+i*5)],'#B5CBC6',.7)
    rail_y=y+h*.35
    line([(x+9,rail_y),(x+w-10,rail_y)],MUTED,3)
    for xx in range(30,int(w),56):
        line([(x+xx,rail_y),(x+xx,rail_y+24)],MUTED,2)
    left,right=w*.39,w*.66
    road_y=y+h*.59
    for a,b in [(0,left),(right,w)]:
        poly([(x+a,road_y),(x+b,road_y-2),(x+b,road_y+7),
              (x+a,road_y+10)],INK)
        line([(x+a,road_y+1),(x+b,road_y-1)],WHITE,1)
        for xx in range(round(a+20),round(b-8),53):
            line([(x+xx,road_y+9),(x+xx,road_y+30)],MUTED,4)
    # Arch pieces and the gap, without an invented battle scene.
    poly([(x+left+8,road_y+2),(x+left+43,road_y+23),
          (x+left+30,road_y+33),(x+left+5,road_y+17)],MUTED,INK,.8)
    poly([(x+right-72,road_y+27),(x+right-21,road_y+33),
          (x+right-5,road_y+19),(x+right-27,road_y+11)],MUTED,INK,.8)
    line([(x+left+40,road_y+28),(x+left+57,road_y+1),
          (x+left+80,road_y+20),(x+right-23,road_y+30)],INK,3)
    for yy in [h*.84,h*.93]:
        wave(x+7,y+yy,w-14,TEAL,1.5,37,.7)
    box((x+12,y+7,x+236,y+27),WHITE)
    text(x+19,y+10,'KERCH STRAIT · ROAD SPAN',12,'bold',TEAL)
    box((x+w-186,y+h-29,x+w-12,y+h-8),WHITE)
    text(x+w-179,y+h-26,'ROAD ARCH COLLAPSED',12,'bold',RED)


def gulf_card(x,y,w,h):
    box((x,y,x+w,y+h),'#E9DDC4')
    sun(x+w-17,y+15,8)
    poly([(x+17,y+h-8),(x+50,y+h-8),(x+34,y+31)],INK)
    ellipse((x+14,y+16,x+56,y+37),None,INK,2)
    line([(x+20,y+20),(x+50,y+32)],INK,1.6)
    for i in range(3):
        d.arc(tuple(round(v*SCALE) for v in
                    (x+40+i*10,y+5-i*5,x+86+i*10,y+45+i*6)),
              232,313,fill=TEAL,width=round(1.4*SCALE))
    plane(x+96,y+20,.38)
    line([(x+64,y+56),(x+81,y+35)],WHITE,2)
    text(x+126,y+10,'INTERCEPTED',18,'bold',TEAL)
    text(x+127,y+36,'Bahrain / US account',11,'sans',MUTED)


def measles_card(x,y,w,h):
    box((x,y,x+w,y+h),'#E8DAD4')
    cx,cy=x+33,y+30
    for a in range(10):
        ang=a*pi/5
        line([(cx+cos(ang)*15,cy+sin(ang)*15),
              (cx+cos(ang)*23,cy+sin(ang)*23)],RED,1.7)
        sun(cx+cos(ang)*23,cy+sin(ang)*23,2,RED)
    ellipse((cx-16,cy-16,cx+16,cy+16),RED)
    for a,b in [(-6,-6),(6,-1),(-2,7)]:sun(cx+a,cy+b,2.5,WHITE)
    text(x+78,y+6,'3 COUNTRIES',22,'bold',RED)
    text(x+79,y+32,'US · MEXICO · BOLIVIA',14,'bold')
    text(x+79,y+49,'PAHO announcement',9,'sans',MUTED)


def climate_card(x,y,w,h):
    box((x,y,x+w,y+h),PALE)
    globe(x+35,y+30,22)
    box((x+83,y+10,x+191,y+51),WHITE,INK,.8)
    text(x+97,y+16,'COP31',25,'bold',TEAL)
    for yy in [43,47]:line([(x+97,y+yy),(x+177,y+yy)],RULE,.8)
    for xx in [218,248,277]:
        ellipse((x+xx-4,y+12,x+xx+4,y+20),INK)
        line([(x+xx,y+22),(x+xx,y+40)],INK,4)
    line([(x+207,y+42),(x+288,y+42)],INK,3)
    for xx in [212,284]:line([(x+xx,y+43),(x+xx,y+55)],INK,1.5)


def sudan_card(x,y,w,h):
    box((x,y,x+w,y+h),'#EBDDD0')
    text(x+10,y+4,'2,230+',33,'title',RED)
    text(x+11,y+43,'CIVILIANS KILLED',10,'bold')
    text(x+149,y+9,'1,630+ by drones',16,'bold',RED)
    text(x+150,y+32,'JAN–OCT 2026',11,'bold')
    text(x+150,y+49,'UN verified · new report',9,'sans',MUTED)


def quad_card(x,y,w,h):
    box((x,y,x+w,y+h),'#D6E4E0')
    for i,country in enumerate(['US','AU','IN','JP']):
        xx=x+17+i*73
        flag(xx,y+8,47,29,country)
        centered(xx+23.5,y+41,country,10,'bold')
    for yy in [53,58]:wave(x+8,y+yy,w-16,TEAL,1.4,37,.7)


def earnings_card(x,y,w,h):
    box((x,y,x+w,y+h),'#DDE2CB')
    box((x+17,y+9,x+78,y+51),INK,radius=3)
    box((x+28,y+17,x+66,y+43),TEAL,WHITE,.7)
    text(x+35,y+21,'AI',18,'bold',WHITE)
    for yy in range(15,52,9):
        for a,b in [(9,16),(79,86)]:line([(x+a,y+yy),(x+b,y+yy)],INK,2)
    for xx in range(24,78,10):
        for a,b in [(3,8),(52,58)]:line([(x+xx,y+a),(x+xx,y+b)],INK,2)
    text(x+102,y+3,'$115.8bn',33,'title',TEAL)
    text(x+104,y+42,'Q3 SALES · +103% Y/Y',14,'bold')


def tariffs_card(x,y,w,h):
    box((x,y,x+w,y+h),'#E8D8CB')
    box((x+13,y+7,x+51,y+31),WHITE)
    for a,b in [(13,21),(43,51)]:box((x+a,y+7,x+b,y+31),RED)
    leaf=[(0,-10),(3,-4),(7,-6),(5,-1),(10,1),(6,5),(7,8),
          (2,7),(1,12),(-1,12),(-2,7),(-7,8),(-6,5),(-10,1),
          (-5,-1),(-7,-6),(-3,-4)]
    poly([(x+32+a*.65,y+18+b*.65) for a,b in leaf],RED)
    box((x+w-51,y+7,x+w-13,y+31),RED)
    star(x+w-40,y+16,5,GOLD)
    centered(x+w/2,y+8,'SELECTED TARIFF RELIEF',13,'bold',TEAL)
    line([(x+69,y+28),(x+w-69,y+28)],TEAL,1.5)
    for direction,xx in [(1,x+69),(-1,x+w-69)]:
        poly([(xx,y+28),(xx+direction*6,y+24),(xx+direction*6,y+32)],TEAL)
    for i,color in enumerate([TEAL,GOLD,RED]):
        box((x+111+i*22,y+33,x+131+i*22,y+44),color,INK,.5)
    box((x+183,y+31,x+197,y+44),WHITE,INK,.5)
    poly([(x+81,y+44),(x+218,y+44),(x+203,y+55),(x+96,y+55)],INK)
    wave(x+8,y+58,w-16,TEAL,1.2,37,.6)


def amazon_card(x,y,w,h):
    box((x,y,x+w,y+h),'#D8E2C9')
    for cx,cy,r in [(20,17,17),(52,13,21),(84,19,21),
                    (116,14,20),(148,20,22),(184,14,20)]:
        line([(x+cx,y+cy),(x+cx,y+h-6)],'#6C7753',3)
        ellipse((x+cx-r,y+cy-r,x+cx+r,y+cy+r),TEAL)
        line([(x+cx-r*.5,y+cy+2),(x+cx+r*.5,y+cy+2)],'#56908A',.7)
    box((x+213,y+45,x+w,y+h),'#C8AD80')
    line([(x+208,y+5),(x+208,y+h-4)],RED,1.7)
    for xx in [227,250,275]:
        box((x+xx,y+42,x+xx+9,y+54),'#8D6D4F')
        ellipse((x+xx,y+40,x+xx+9,y+45),PAPER,INK,.5)
    text(x+224,y+9,'AWÁ',20,'bold',TEAL)
    text(x+224,y+31,'BRAZIL',10,'bold',MUTED)


def score_card(x,y,w,h):
    box((x,y,x+w,y+h),'#D9E5D5')
    ellipse((x+16,y+10,x+57,y+51),WHITE,INK,1)
    poly([(x+29,y+19),(x+43,y+19),(x+46,y+32),
          (x+36,y+40),(x+25,y+31)],INK)
    for a,b in [(20,14),(53,17),(21,45),(54,46)]:
        line([(x+a,y+b),(x+36,y+30)],INK,.6)
    text(x+77,y+2,'7–0',47,'title',TEAL)
    text(x+210,y+9,'BRAZIL',15,'bold')
    text(x+210,y+32,'SINGAPORE',12,'bold',MUTED)
    text(x+78,y+50,'VINICIUS HAT-TRICK · FRIENDLY',9,'bold',TEAL)


def feature(x,y,number,region,headline,scene,caption,color=TEAL):
    text(x,y,f'{number:02d} / {region}',11,'bold',color)
    assert width(headline,28.5,'title')<=302, headline
    text(x,y+18,headline,28.5,'title')
    illustration(scene,x,y+53,302,60,native_w=302,native_h=60)
    bottom=paragraph(x,y+120,caption,302,16,18)
    assert bottom<=y+156, (number,bottom-y)


def location_map(x,y,w,h):
    """Original, simplified coastlines; pins link to numbered news below."""
    box((x,y,x+w,y+h),'#DFE8E1')
    def point(lon,lat):
        return x+(lon+180)/360*w,y+(78-lat)/139*h
    for lon in [-120,-60,0,60,120]:
        line([point(lon,78),point(lon,-61)],'#CCDAD3',.6)
    for lat in [-30,0,30,60]:
        line([point(-180,lat),point(180,lat)],'#CCDAD3',.6)
    continents=[
        [(-168,66),(-151,71),(-128,70),(-113,74),(-98,75),(-78,72),
         (-60,57),(-66,48),(-82,26),(-88,18),(-84,10),(-98,18),
         (-112,30),(-124,40),(-135,56),(-153,59)],
        [(-72,60),(-49,61),(-23,75),(-40,82),(-64,80)],
        [(-81,12),(-68,11),(-58,6),(-50,-1),(-36,-7),(-41,-23),
         (-54,-34),(-65,-55),(-73,-50),(-75,-32),(-81,-6)],
        [(-10,36),(-10,44),(-3,49),(4,53),(8,58),(16,70),(30,71),
         (42,68),(58,72),(90,76),(123,72),(159,64),(176,60),
         (165,52),(147,44),(133,36),(121,22),(111,19),(107,9),
         (99,2),(95,17),(80,8),(71,22),(58,25),(51,12),(42,14),
         (35,30),(29,36),(22,37),(17,42),(10,44),(3,41)],
        [(-17,14),(-16,30),(-6,36),(9,37),(24,32),(34,31),(43,12),
         (51,11),(45,-3),(38,-17),(28,-34),(17,-35),(11,-20),
         (8,3),(-1,5),(-10,7)],
        [(113,-22),(124,-14),(135,-12),(144,-18),(153,-27),
         (146,-39),(131,-32),(114,-34)],
        [(130,-3),(146,-5),(153,-10),(140,-9)],
        [(96,5),(107,-7),(116,-8),(111,-3)],
        [(119,18),(125,8),(124,4),(120,8)],
        [(130,31),(136,35),(141,41),(145,44),(142,36),(136,31)],
        [(47,-13),(50,-17),(47,-25),(44,-21)],
        [(166,-35),(175,-40),(172,-45),(167,-43)],
        [(-8,50),(-3,59),(1,58),(2,51)],
    ]
    for coast in continents:poly([point(*p) for p in coast],TEAL)
    # The map links only selected locations; it neither draws borders nor
    # purports to inventory every location mentioned in the day's stories.
    for number,lon,lat,dx,dy in [
        (1,36.5,45.3,-12,-11),(3,-102,24,-8,-4),
        (5,32,15,-14,9),(6,121,15,8,-4),(20,151,-34,3,12),
    ]:
        px,py=point(lon,lat)
        sun(px,py,2.4,RED)
        cx,cy=px+dx,py+dy
        line([(px,py),(cx,cy)],RED,.7)
        ellipse((cx-8,cy-8,cx+8,cy+8),WHITE,RED,.8)
        centered(cx,cy-5.3,str(number),9,'bold',RED)


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,default=ROOT/'entry.png')
args=parser.parse_args()

# A recognisable front page: large dated masthead, one lead, an indexed world
# map, nine illustrated reports and nine concise briefs across regions.
box((18,18,1006,1006),None,INK,1)
text(32,30,'THE WORLD, IN ONE DAY',12,'bold',TEAL)
text(32,46,'WORLD DAILY',53,'title')
box((652,30,992,101),INK)
centered(822,39,'TUESDAY',13,'bold',SEA)
centered(822,60,'17 NOVEMBER 2026',29,'bold',WHITE)
text(32,105,'20 reports · War & diplomacy · Health & science · Climate · Trade · Sport',15,'italic',MUTED)
line([(32,129),(992,129)],INK,2.5)

text(32,140,'01 / EUROPE · UKRAINE & RUSSIA',12,'bold',RED)
text(32,159,'Ukraine hits Kerch bridge',41,'title')
assert width('Ukraine hits Kerch bridge',41,'title')<=631
illustration(lead_scene,32,210,631,86,native_w=631,native_h=86)
paragraph(32,304,'Road arch collapses; Kyiv bridges struck, mayor says.',631,17.5,20)
text(32,326,'REUTERS · 17 NOV · SCHEMATIC',9,'sans',MUTED)

text(690,140,'WORLD / SELECTED STORY LOCATIONS',11,'bold',TEAL)
location_map(690,163,302,101)
text(690,275,'20 / OCEANIA · AUSTRALIA',11,'bold',TEAL)
text(690,292,'New RBA minutes: 6–3 split',20,'bold')
paragraph(690,316,'Nov 3 vote lifted rate to 4.85%.',302,14,16,MUTED)
line([(676,140),(676,333)],RULE,.7)
line([(32,342),(992,342)],INK,1.4)

xs=[32,361,690]
for xx in [347,676]:line([(xx,355),(xx,838)],RULE,.7)
for yy in [515,679,843]:line([(32,yy),(992,yy)],RULE,.8)

feature(xs[0],355,2,'MIDDLE EAST · IRAN / BAHRAIN',
        'Iran drones; US strike',gulf_card,
        'Bahrain reports interception; US official says launch site hit.',RED)
feature(xs[1],355,3,'PUBLIC HEALTH · AMERICAS',
        'Measles elimination lost',measles_card,
        'US, Mexico and Bolivia lose elimination status, PAHO says.',RED)
feature(xs[2],355,4,'CLIMATE · ANTALYA, TÜRKIYE',
        'COP31 draft divides',climate_card,
        'No final deal: finance and fossil fuels divide ministers.')

feature(xs[0],519,5,'AFRICA · SUDAN',
        'Sudan’s civilian toll',sudan_card,
        'UN releases Jan–Oct count; most documented deaths by drones.',RED)
feature(xs[1],519,6,'INDO-PACIFIC · MANILA',
        'Quad leaders meet',quad_card,
        'US, Australia, India, Japan: maritime, AI and cable projects.')
feature(xs[2],519,7,'BUSINESS · UNITED STATES',
        'Nvidia sales double',earnings_card,
        'AI drives Q3 revenue up 103%; earnings released today.')
feature(xs[0],683,8,'TRADE · CANADA & CHINA',
        'Xi & Carney ease tariffs',tariffs_card,
        'Selected export relief; steel and aluminium exemptions extended.')
feature(xs[1],683,9,'AMAZON · BRAZIL',
        'Awá footage: forest fears',amazon_card,
        'Funai reviews footage; advocates warn of threats from logging.')
feature(xs[2],683,12,'FOOTBALL · SINGAPORE',
        'Brazil 7–0 Singapore',score_card,
        'Vinicius nets first-half hat-trick in the friendly win.')

# Readable briefs retain secondary stories; no story count is a quality claim.
# Their date/period and attribution distinctions survive the shorter wording.
text(32,851,'ALSO TODAY / ACROSS REGIONS & FIELDS',10,'bold',TEAL)
briefs=[
    (10,'MONGOLIA','President says he’ll resign',
     'Khurelsukh denies graft; parliament decides.'),
    (11,'JAPAN / TAIWAN','Japan protests air breach',
     'Believed Russian; Taiwan detects planes.'),
    (13,'MOZAMBIQUE','Mondlane trial opens',
     'Unrest charges; he denies them.'),
    (14,'UK / JUL–SEP DATA','Pay growth slows to 3.5%',
     'New ONS release; jobless rate 4.6%.'),
    (15,'TECHNOLOGY','OpenAI releases GPT-6.2',
     'Astra and Sol models launched today.'),
    (16,'NIGERIA / AGENCY REPORT','Drug agency reports 8 arrests',
     'October operation; Sahara route.'),
    (17,'SCIENCE / LEUKEMIA TRIAL','Sellas reports survival gain',
     'Experimental vaccine; Phase 3 endpoint met.'),
    (18,'PERU / CHINA','El Niño assistance pledged',
     'Fujimori says China offered $22.5m.'),
    (19,'INDONESIA','Police official dismissed',
     'Alleged phone spying on president.'),
]
# Four columns would make these headlines too small. Three columns allow 20px
# type; each compact brief fits its own two-line block without clipping.
for i,(number,region,headline,detail) in enumerate(briefs):
    xx=xs[i%3]
    yy=869+(i//3)*44
    text(xx,yy,f'{number:02d} / {region}',9.5,'bold',TEAL)
    assert width(headline,20,'bold')<=302, (number,headline)
    text(xx,yy+12,headline,20,'bold')
    assert width(detail,11.5)<=302, (number,detail)
    text(xx,yy+32,detail,11.5,'sans',MUTED)

canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(args.out,optimize=True)
print('Rendered',args.out)
