import re

import scrapy
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import re
import pprint
from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *
import hashlib
import datetime


class TikTokSpider(VideoSpider):
    name = 'musically'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'musically'
    input_type = INPUT_TYPE_CRAWL

    download_delay = 0
    hd = {
        'build': '1516788764802',
        'language': 'zh_CN',
        'X-Request-Info5': 'eyJvcyI6ImFuZHJvaWQgNy4xLjEiLCJ2ZXJzaW9uIjoiNi41LjAiLCJzbGlkZXItc2hvdy1jb29raWUiOiJibDgyTlRFMk16azJNemN4TWpNek1qRTFOVEF6T2tOa1NGSTBjWEpaU0d4M2IxbFZkV3R3VEdVeWVXYzlQVHBoTUdabE1tUTVNbVkwTURRMFpEQmxaV0l6WmpFMU56TTVaRFEwTUdNek5EbzJOVEUyTXprMk16Y3hNak16TWpFMU5UQXoiLCJYLVJlcXVlc3QtSUQiOiI1Y2Y3ODgzYS04MDE4LTRlZDgtOWQ3NC04MDRlZjIwMjE3ZGMiLCJtZXRob2QiOiJHRVQiLCJ1cmwiOiJodHRwczpcL1wvYXBpLm11c2ljYWwubHlcL3Jlc3RcL3VzZXJcLzI2NDg5ODAzNTk4ODUyMDk2MD91c2VyX3ZvX3JlbGF0aW9ucz1hbGwiLCJvc3R5cGUiOiJhbmRyb2lkIiwiZGV2aWNlaWQiOiJhMGQ3MGU5ZDExYjk1OTQ2NmE5NDI0MmY5NjA4NmVhZGM3NTU0OSIsInRpbWVzdGFtcCI6MTUxNzIxODM1NjgyMH0=',
        'X-Request-Sign5': '01a6d89754cd16765203fc8e5d98967c26d8509e6b5e',
        'Authorization': 'M-TOKEN "hash"="NWNhYTdjZTkwMDAxMDAwZmUwNGRiNTcxNmIwMDE0MGYyZDM4ZmRjNTBkMDM0MGZlYzA1N2Q5ZWIxYjkzMzBiMTZiNDcxYTNlMWU4MmVlOGEzMjJlMmZmZWU1ZjIzYjVjNjIwYTkwYmUwM2IxYmNlMzYwNTA1NmRjZTJlNDU2YzkwYWZlZDVmYTczNDYyMzJkYmRlMTExYTQyODkyYmExMzc0OWE0YTRjMzkwYWRjMDM1NGJiNDQzYzI4OThhZGFkMWYwYzBkODY0ZTA3ZmM5M2IzYjAzZmRmODU0NTcxNzBmYzhiYzhhZTgzMGFmMjQyNGJjMTlmMzkxNmE0YzliNDJmZTZlM2EzOWJhMGI4NWJhMWE3ZDY4OTcyYjQ1NmQ1ZDI2ZGEzNGQ5YWVjOGE4ZTZmM2QyNzVmYmQ3ZmJiMTU5MDAzYTAwOThmNjU1M2JiODY4NDdmYmUwMjBhNDNlYWQ3ZGZlZjU5MmNhZDQwNjU3MjMwZjQ1OWY4NDdjMDkxZGIxYmViNDU1MTRlZGFmOA=="',
    }
    page = 0
    max_count = 20
    # channel_list = get_channel_list('like', 'Thailand')
    channel_list = [
        {'url': 'https://m.tiktok.com/v/6569929131457252614.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/6569929131457252614.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/6586657878122188037.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6589974705418013957.html', 'tags': ['animal', 'girl']},
        {'url': 'https://m.tiktok.com/v/6589628452918267142.html', 'tags': ['girl']},
        {'url': 'https://m.tiktok.com/v/6592659156853853446.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6592413940108496134.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6590401312242797830.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6589317852266761478.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6592542249010072838.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6590644809306737925.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6589407416947838213.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/6577022746847350022.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/6588585770485812485.html', 'tags': ['food', 'music']},
        {'url': 'https://m.tiktok.com/v/6587126432370003206.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6587894636784651526.html', 'tags': ['music', 'animal']},
        {'url': 'https://m.tiktok.com/v/6581469195865689350.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6587410645128318213.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6584996174967606533.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6585193618909170949.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6534256964296250368.html', 'tags': ['magic']},
        {'url': 'https://m.tiktok.com/v/6564368825083497733.html', 'tags': ['music', 'interest']},
        {'url': 'https://m.tiktok.com/v/6562798427183254790.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6585031647479991558.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6582722128745860358.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6586399370566962437.html', 'tags': ['baby', 'interst']},
        {'url': 'https://m.tiktok.com/v/6591161406316350726.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6579607426209680645.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6579603215870872838.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6574035297984580870.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/6576147027107777797.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6581883974262459653.html', 'tags': ['vehicle']},
        {'url': 'https://m.tiktok.com/v/6568536071892634885.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6589197338630163713.html', 'tags': ['cartoon']},
        {'url': 'https://m.tiktok.com/v/6579766683127254278.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6579371089523117317.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6566765988501523718.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6576919993995234565.html', 'tags': ['animal']},
        {'url': 'https://m.tiktok.com/v/6571144520593837317.html', 'tags': ['music', 'comedy']},
        {'url': 'https://m.tiktok.com/v/6578507944889945349.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6566954192080997638.html', 'tags': ['life', 'food']},
        {'url': 'https://m.tiktok.com/v/6585921222117166342.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6583277317362027781.html', 'tags': ['interest', 'beauty']},
        {'url': 'https://m.tiktok.com/v/6592545802969681158.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6567000243672452358.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6592152994723138822.html', 'tags': ['sport']},
        {'url': 'https://m.tiktok.com/v/6592228061956017413.html', 'tags': ['fashion']},
        {'url': 'https://m.tiktok.com/v/6581420248761634053.html', 'tags': ['dance', 'guy']},
        {'url': 'https://m.tiktok.com/v/6560857100862360837.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6581019235223342341.html', 'tags': ['interst']},
        {'url': 'https://m.tiktok.com/v/6569184961704758533.html', 'tags': ['fitness']},
        {'url': 'https://m.tiktok.com/v/6579155737736400134.html', 'tags': ['fitness']},
        {'url': 'https://m.tiktok.com/v/6579239243925703941.html', 'tags': ['sport']},
        {'url': 'https://m.tiktok.com/v/6571011342898040070.html', 'tags': ['sport']},
        {'url': 'https://m.tiktok.com/v/6583244356117859589.html', 'tags': ['sport']},
        {'url': 'https://m.tiktok.com/v/6588265042519526662.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/6575648272386362630.html', 'tags': ['nature']},
        {'url': 'https://m.tiktok.com/v/6581187986317135110.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/188162498372628480.html', 'tags': ['music', 'guy']},
        {'url': 'https://m.tiktok.com/v/183911473834864640.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/210271140672577536.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/202677941393154048.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/6517751830884127744.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/248957577928073216.html', 'tags': ['dance', 'interest']},
        {'url': 'https://m.tiktok.com/v/274401412393132032.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6535503875217052672.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/6591092931891825926.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6568889797287349510.html', 'tags': ['guy']},
        {'url': 'https://m.tiktok.com/v/6568609165319605509.html', 'tags': ['guy']},
        {'url': 'https://m.tiktok.com/v/260700977911967744.html', 'tags': ['intersest']},
        {'url': 'https://m.tiktok.com/v/256319757480558592.html', 'tags': ['interest']},
        {'url': 'https://m.tiktok.com/v/168536242484064256.html', 'tags': ['music', 'guy']},
        {'url': 'https://m.tiktok.com/v/260042274464849920.html', 'tags': ['music', 'guy']},
        {'url': 'https://m.tiktok.com/v/248416887464890368.html', 'tags': ['music', 'interest']},
        {'url': 'https://m.tiktok.com/v/201665145469550592.html', 'tags': ['music', 'interest']},
        {'url': 'https://m.tiktok.com/v/6553010058043593743.html', 'tags': ['talent', 'music']},
        {'url': 'https://m.tiktok.com/v/232027772674605056.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/53010275779518465.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/299888749465968640.html', 'tags': ['beauty', 'music']},
        {'url': 'https://m.tiktok.com/v/284173589204058112.html', 'tags': ['beauty', 'music']},
        {'url': 'https://m.tiktok.com/v/125168149292883968.html', 'tags': ['music']},
        {'url': 'https://m.tiktok.com/v/45070660757917696.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/47966776.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6548617911324382208.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/209481591864352768.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/219042779904065536.html', 'tags': ['animal', 'beauty']},
        {'url': 'https://m.tiktok.com/v/316549936257613824.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/283103159877738496.html', 'tags': ['comedy', 'beauty']},
        {'url': 'https://m.tiktok.com/v/266201596949417984.html', 'tags': ['relationship']},
        {'url': 'https://m.tiktok.com/v/6552135489070044175.html', 'tags': ['fashion']},
        {'url': 'https://m.tiktok.com/v/6528822906070242304.html', 'tags': ['dance']},
        {'url': 'https://m.tiktok.com/v/6527809423232996367.html', 'tags': ['music']},
        {'url': 'https://m.tiktok.com/v/237108383747723264.html', 'tags': ['music']},
        {'url': 'https://m.tiktok.com/v/6572982332553170182.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/6558884261695329295.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/6563183362737982725.html', 'tags': ['beauty']},
        {'url': 'https://m.tiktok.com/v/209805673235103744.html', 'tags': ['beauty', 'dance']},
        {'url': 'https://m.tiktok.com/v/6572634489799838981.html', 'tags': ['girl', 'interest']},
        {'url': 'https://m.tiktok.com/v/6539564951084733455.html', 'tags': ['comedy']},
        {'url': 'https://m.tiktok.com/v/6599472724823772418.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6580766810633669893.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6599636862103457030.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6600194599082265870.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6576331606825372933.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6596401293311347974.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6572398260915277062.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6598083309866061062.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6592542249010072838.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6598402106271468806.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6600133115467795717.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6589552883048385797.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6590604423339183361.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6571874367712529669.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6594850987880484101.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6596247375780515077.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6572227744774491398.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6568098470765268230.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6591498356650937605.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6577279918948748550.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6597536497363062021.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6597536497363062021.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595656227898789125.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6592208326824561926.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6578910376102990863.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6589722240944704774.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6600577358581730566.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6591558645635353862.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6600428623478394118.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6576346684140293382.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6600812221364702470.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6596083104840944902.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6599762019035909381.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6586950504553647366.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6589665309110570245.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6581471051891346693.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6596740460415290629.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6587053667130543366.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6568973869959351557.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595900009361706246.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6601222425537416453.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6596609467159153925.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6576345239202581765.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6568917883059965190.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6569214558869654789.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6586474743472475397.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6574881847942057222.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6589966790170774790.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6591559580621212934.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6594500094823763205.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6593010826070723846.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6587003145002421510.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6568550579772067077.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6594505934792297734.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6577751353538383109.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6572206990943063301.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6592404162560920837.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6599760579521416453.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6569045637252254982.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6598961130750610694.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6567486392836820229.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6577768797137014021.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6579200363272867078.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595484392213187846.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6573529470215392517.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6586672363302030598.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6569540344470310149.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6575680291359165702.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6592172841951563014.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6577417614354550022.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6567995719070780677.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6592535863958195461.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6593902873275272454.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6587437872079457542.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6598266276555001094.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6580403832839212293.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6575579193017371910.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595908998862474501.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6585973668520660230.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595266639577484549.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6572319163853835525.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6571703076095266054.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6568613042488085766.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6575577751695133958.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6594485524545670405.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595779111010962694.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6570601083503119622.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6584604409248877829.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6571825892010495238.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6595822656602246405.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6579728574788406533.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6576299290216369414.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6572942788378234117.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6567433721593466117.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6576267039994809605.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6573264163580153093.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6589709969401056517.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6590619945082555653.html', 'tags': []},
        {'url': 'https://m.tiktok.com/v/6579255802584894726.html', 'tags': []},
    ]

    def __init__(self, *a, **kw):
        super(TikTokSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        raw = dict()
        temp = self.channel_list.pop(0)
        raw['source_url'] = temp['url']
        raw['tags'] = temp['tags']

        if self.is_source_url_exist(self.input_type, raw['source_url']):
            self.logger.info('source_url exists: ' + str(raw['source_url']))
            self.spider_idle()
        elif self.is_source_url_invalid(raw['source_url']):
            self.spider_idle()
        else:
            yield Request(
                raw['source_url'],
                meta=raw,
                headers=self.hd,
                dont_filter=True,
                callback=self.parse_page
            )

    def parse_list(self, response):
        pass

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        # print response.body_as_unicode()
        tjson = json.loads(re.findall('var data = (.*?)\};', response.body_as_unicode())[0] + "}")
        # tjson = json.loads(re.findall('var data = (.*?)}];', response.body_as_unicode())[0] + "}]")[0]
        if tjson['video']['has_watermark']:
            self.logger.warning('watermark warning!!!!!!!!')
        elif not tjson['desc']:
            self.logger.warning('empty title !!!!!')
        else:
            raw['source_url'] = response.url
            raw['publisher_id'] = tjson['author']['uid']
            raw['publisher'] = tjson['author']['nickname']
            raw['publisher_icon'] = ["https:" + tjson['author']['avatar_thumb']['url_list'][0]]
            raw['publish_ts'] = tjson['create_time']
            raw['title'] = tjson['desc']
            raw['video'] = "https:" + tjson['video']['play_addr']['url_list'][0]
            raw['doc_id'] = tjson['aweme_id']
            raw['thumbnails'] = ["https:" + tjson['video']['cover']['url_list'][0]]
            raw['video_height'] = tjson['video']['height']
            raw['video_width'] = tjson['video']['width']

            raw['like_count'] = tjson['statistics']['digg_count']
            raw['share_count'] = tjson['statistics']['share_count']
            raw['view_count'] = tjson['statistics']['play_count']
            raw['comment_count'] = tjson['statistics']['comment_count']
            raw['duration'] = -1
            raw['keywords'] = []
            for item in tjson['text_extra']:
                if 'hashtag_name' in item:
                    raw['keywords'].append(item['hashtag_name'])

            raw['extra_info'] = dict()
            raw['extra_info']['raw_doc_id'] = tjson['aweme_id']
            raw['extra_info']['raw_publisher_id'] = tjson['author']['uid']
            self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(TikTokSpider, self).generate_message(article_info)
        if message:
            if 'inlinks' in article_info['raw']:
                message['inlinks'] = article_info['raw']['inlinks']
            return message

    def duration_gen(self, sb):
        try:
            minute, second = sb.split(":")
            return float(int(minute) * 60 + int(second))
        except:
            return 100000000

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_doc_id_from_raw(self, raw):
        return hashlib.md5(raw['doc_id']).hexdigest()

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_content_from_raw(self, raw):
        return ""

    def get_duration_from_raw(self, raw):
        return raw['duration']

    def get_video_from_raw(self, raw):
        return raw['video']

    def get_publish_time_from_raw(self, raw):
        time = datetime.datetime.fromtimestamp(raw['publish_ts'])
        return str(time)[:19]

    def get_keywords_from_raw(self, raw):
        return raw['keywords']

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_source_name_from_raw(self, raw):
        return self.source_name

    def get_video_height_from_raw(self, raw):
        return raw['video_height']

    def get_video_width_from_raw(self, raw):
        return raw['video_width']

    def get_extra_from_raw(self, raw):
        return raw['extra_info']

    def get_video_id_from_raw(self, raw):
        return raw['doc_id']

    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    def get_publisher_id_from_raw(self, raw):
        return hashlib.md5(raw['publisher_id']).hexdigest()

    def get_video_type_from_raw(self, raw):
        return VIDEO_TYPE_SMALL_VIDEO

    def get_input_type_from_raw(self, raw):
        return self.input_type

    def get_like_count_from_raw(self, raw):
        return raw['like_count']

    def get_comment_count_from_raw(self, raw):
        return raw['comment_count']

    def get_share_count_from_raw(self, raw):
        return raw['share_count']

    def get_view_count_from_raw(self, raw):
        return raw['view_count']
