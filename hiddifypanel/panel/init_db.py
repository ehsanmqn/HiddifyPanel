from hiddifypanel.models import  *
from hiddifypanel.panel.database import db



from hiddifypanel.panel.database import db
from dateutil import relativedelta
import datetime
from hiddifypanel.models import *
from hiddifypanel.panel import hiddify
import random
import uuid
import urllib
import string
def init_db():
    
    

    db.create_all()
    
    # db.engine.execute(f'ALTER TABLE child ADD COLUMN ip integer')
    try:
        column_type = User.start_date.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE user ADD COLUMN start_date {column_type}')
        column_type = User.package_days.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE user ADD COLUMN package_days {column_type}')
    except:
        pass
    try:
        column_type = Child.unique_id.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE child ADD COLUMN unique_id {column_type}')
        column_type = Domain.alias.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE domain ADD COLUMN alias {column_type}')
        column_type = Domain.child_id.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE domain ADD COLUMN child_id {column_type} DEFAULT 0')
        column_type = Proxy.child_id.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE proxy ADD COLUMN child_id {column_type} DEFAULT 0')
        column_type = BoolConfig.child_id.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE bool_config ADD COLUMN child_id {column_type} DEFAULT 0')
        column_type = StrConfig.child_id.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE str_config ADD COLUMN child_id {column_type} DEFAULT 0')
    except:pass

    if len(Domain.query.all())!=0 and BoolConfig.query.count()==0:
        db.engine.execute(f'DROP TABLE bool_config')
        db.engine.execute(f'ALTER TABLE bool_config_old RENAME TO bool_config')
    if len(Domain.query.all())!=0 and StrConfig.query.count()==0:
        db.engine.execute(f'DROP TABLE str_config')
        db.engine.execute(f'ALTER TABLE str_config_old RENAME TO str_config')

    try:
        db.engine.execute('ALTER TABLE user ADD COLUMN monthly BOOLEAN')
        db.engine.execute('ALTER TABLE user RENAME COLUMN monthly_usage_limit_GB TO usage_limit_GB')       
    except:
        pass
    try:
        db.engine.execute(f'update str_config set child_id=0 where child_id is NULL')
        db.engine.execute(f'update bool_config set child_id=0 where child_id is NULL')
        db.engine.execute(f'update domain set child_id=0 where child_id is NULL')
        db.engine.execute(f'update proxy set child_id=0 where child_id is NULL')
        column_type = Domain.cdn_ip.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE domain ADD COLUMN cdn_ip {column_type}')
    except:
        pass
    
    db_version=int(hconfig(ConfigEnum.db_version) or 0) 
    start_version=db_version
    # print(f"Current DB version is {db_version}")
    if not Child.query.filter(Child.id==0).first():
        print(Child.query.filter(Child.id==0).first())
        db.session.add(Child(unique_id="self",id=0))
        db.session.commit()
    db_actions={1:_v1,2:_v2,3:_v3,6:_v6,8:_v8,9:_v9,10:_v10,11:_v11,12:_v12,13:_v13,14:_v14,16:_v16,17:_v17,19:_v19}
    for ver,db_action in db_actions.items():
        if ver<=db_version:continue
        if start_version==0 and ver==10:continue
        print(f"Updating db from version {db_version}")
        db_action()
        
        print(f"Updated successfuly db from version {db_version} to {ver}")
        db_version=ver
        db.session.commit()
        set_hconfig(ConfigEnum.db_version,db_version,commit=False)
    # 
    if hconfig(ConfigEnum.is_parent) and ParentDomain.query.count()==0:
        external_ip=hiddify.get_ip(4)
        db.session.add(ParentDomain(domain=f"{external_ip}.sslip.io",show_domains=[]))
    db.session.commit()
    return BoolConfig.query.all()

def _v19():
    set_hconfig(ConfigEnum.path_trojan,get_random_string(7,15))
    set_hconfig(ConfigEnum.path_vless,get_random_string(7,15))
    set_hconfig(ConfigEnum.path_vmess,get_random_string(7,15))
    set_hconfig(ConfigEnum.path_ss,get_random_string(7,15))

    set_hconfig(ConfigEnum.path_grpc,get_random_string(7,15))
    set_hconfig(ConfigEnum.path_tcp,get_random_string(7,15))
    set_hconfig(ConfigEnum.path_ws,get_random_string(7,15))
    

def _v17():
    for u in User.query.all():
        if u.expiry_time:
            if not u.package_days:
                if not u.last_reset_time:
                    u.package_days=(u.expiry_time-datetime.date.today()).days
                    u.start_date=datetime.date.today()
                else:
                    u.package_days=(u.expiry_time-u.last_reset_time).days
                    u.start_date=u.last_reset_time
            u.expiry_time=None
            
            


def _v16():
    try:
        if BoolConfig.query.filter(BoolConfig.key==ConfigEnum.tuic_enable).count()==0:
            db.session.add(BoolConfig(key=ConfigEnum.tuic_enable,value=False,child_id=0))
        if BoolConfig.query.filter(BoolConfig.key==ConfigEnum.shadowtls_enable).count()==0:
            db.session.add(BoolConfig(key=ConfigEnum.shadowtls_enable,value=False,child_id=0))
        if StrConfig.query.filter(StrConfig.key==ConfigEnum.shadowtls_fakedomain).count()==0:
            db.session.add(StrConfig(key=ConfigEnum.shadowtls_fakedomain, value="en.wikipedia.org",child_id=0))
    except Exception as e:
        print(e)

        

def _v14():
    db.session.add(StrConfig(key=ConfigEnum.utls,value="chrome",child_id=0))
    
def _v13():
    db.session.add(StrConfig(key=ConfigEnum.telegram_bot_token,value="",child_id=0))
    db.session.add(StrConfig(key=ConfigEnum.package_mode,value="release",child_id=0))

def _v12():
    db.engine.execute(f'drop TABLE child')
    db.create_all()
    db.session.add(Child(id=0,unique_id="default"))

def _v11():
    try:
        column_type = User.last_online.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE user ADD COLUMN last_online {column_type}')
        # db.engine.execute(f'update user set last_online="1000-01-01 00:00:00" where last_online is NULL')
    except:
        pass
    


def get_random_string(min_=10,max_=30):
    # With combination of lower and upper case
    length=random.randint(min_, max_)
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(characters) for i in range(length))
    return result_str


def _v1():
        
        next10year = datetime.date.today() + relativedelta.relativedelta(years=6)
        external_ip=hiddify.get_ip(4)
        
        data = [
            StrConfig(key=ConfigEnum.db_version,value=1),
            User(name="default",usage_limit_GB=9000,package_days=3650),
            Domain(domain=external_ip+".sslip.io",mode=DomainType.direct),
            StrConfig(key=ConfigEnum.admin_secret,value=str(uuid.uuid4())),
            StrConfig(key=ConfigEnum.http_ports,value="80"),
            StrConfig(key=ConfigEnum.tls_ports,value="443"),
            
            StrConfig(key=ConfigEnum.decoy_domain,value="www.wikipedia.org"),
            StrConfig(key=ConfigEnum.proxy_path,value=get_random_string()),
            BoolConfig(key=ConfigEnum.firewall,value=False),
            BoolConfig(key=ConfigEnum.netdata,value=True),
            StrConfig(key=ConfigEnum.lang,value='en'),
            
            BoolConfig(key=ConfigEnum.block_iran_sites,value=True),
            BoolConfig(key=ConfigEnum.allow_invalid_sni,value=True),
            # BoolConfig(key=ConfigEnum.kcp_enable,value=False),
            # StrConfig(key=ConfigEnum.kcp_ports,value="88"),
            BoolConfig(key=ConfigEnum.auto_update,value=True),
            BoolConfig(key=ConfigEnum.speed_test,value=True),
            BoolConfig(key=ConfigEnum.only_ipv4,value=False),

            BoolConfig(key=ConfigEnum.vmess_enable,value=True),
            BoolConfig(key=ConfigEnum.http_proxy_enable,value=True),
            StrConfig(key=ConfigEnum.shared_secret,value=str(uuid.uuid4())),

            BoolConfig(key=ConfigEnum.telegram_enable,value=True),
            # StrConfig(key=ConfigEnum.telegram_secret,value=uuid.uuid4().hex),
            StrConfig(key=ConfigEnum.telegram_adtag,value=""),
            StrConfig(key=ConfigEnum.telegram_fakedomain, value="www.wikipedia.org"),
 
            BoolConfig(key=ConfigEnum.ssfaketls_enable,value=False),
            # StrConfig(key=ConfigEnum.ssfaketls_secret,value=str(uuid.uuid4())),
            StrConfig(key=ConfigEnum.ssfaketls_fakedomain, value="fa.wikipedia.org"),

            # BoolConfig(key=ConfigEnum.shadowtls_enable,value=False),
            # StrConfig(key=ConfigEnum.shadowtls_secret,value=str(uuid.uuid4())),
            # StrConfig(key=ConfigEnum.shadowtls_fakedomain, value="en.wikipedia.org"),

            # BoolConfig(key=ConfigEnum.ssr_enable,value=False),
            # # StrConfig(key=ConfigEnum.ssr_secret,value=str(uuid.uuid4())),
            # StrConfig(key=ConfigEnum.ssr_fakedomain, value="ar.wikipedia.org"),

            # BoolConfig(key=ConfigEnum.tuic_enable,value=False),
            # StrConfig(key=ConfigEnum.tuic_port,value=3048),

            BoolConfig(key=ConfigEnum.domain_fronting_tls_enable,value=False),
            BoolConfig(key=ConfigEnum.domain_fronting_http_enable,value=False),
            StrConfig(key=ConfigEnum.domain_fronting_domain,value=""),

            # BoolConfig(key=ConfigEnum.torrent_block,value=False),

            *get_proxy_rows_v1()
        ]

        # for c in ConfigEnum:
        #     if c in [d.key for d in data if type(d) in [BoolConfig,StrConfig]]:
        #         continue
        #     if c.type()==bool:
        #         data.append(BoolConfig(key=c,value=False))
        #     else:
        #         data.append(StrConfig(key=c,value=""))
                    

        
        db.session.bulk_save_objects(data)

def _v2():
    db.session.bulk_save_objects([
            StrConfig(key=ConfigEnum.telegram_lib,value="python"),
            StrConfig(key=ConfigEnum.admin_lang,value=hconfig(ConfigEnum.lang)),
        ])

def _v3():
        db.session.bulk_save_objects([
            StrConfig(key=ConfigEnum.branding_title,value=""),
            StrConfig(key=ConfigEnum.branding_site,value=""),
            StrConfig(key=ConfigEnum.branding_freetext,value=""),
            BoolConfig(key=ConfigEnum.v2ray_enable,value=False),
        ])

def _v6():
    try:
        Proxy.query.filter(Proxy.name=='tls XTLS direct trojan').delete()
        Proxy.query.filter(Proxy.name=='tls XTLSVision direct trojan').delete()
    except:
        pass
    db.session.bulk_save_objects([
        *make_proxy_rows(["XTLS direct vless"])
    ])

def _v8():
    db.session.bulk_save_objects([
        *make_proxy_rows([
        "grpc direct vless",
        "grpc direct trojan",
        "grpc direct vmess"])
    ])
def _v9():
    try:
        column_type = User.mode.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE user ADD COLUMN mode {column_type}')
        column_type = User.comment.type.compile(db.engine.dialect)
        db.engine.execute(f'ALTER TABLE user ADD COLUMN comment {column_type}')
        
        for u in User.query.all():
            u.mode= UserMode.monthly if u.monthly else UserMode.no_reset
    except:
        pass
    
    db.session.bulk_save_objects(
        [
            BoolConfig(key=ConfigEnum.is_parent,value=False),
            StrConfig(key=ConfigEnum.parent_panel,value=''),
            StrConfig(key=ConfigEnum.unique_id,value=str(uuid.uuid4()))
        ]
    )

def _v10():
    all_configs=get_hconfigs()
    try:
        
        db.engine.execute("ALTER TABLE `str_config` RENAME TO `str_config_old`")
        db.engine.execute("ALTER TABLE `bool_config` RENAME TO `bool_config_old`")
        
    except:
        pass
    db.create_all()
    
    rows=[]
    
    for c,v in all_configs.items():
        if c.type()==bool:
            rows.append(BoolConfig(key=c,value=v,child_id=0))
        else:
            rows.append(StrConfig(key=c,value=v,child_id=0))
    
    db.session.bulk_save_objects(rows)
    




def get_proxy_rows_v1():
    return make_proxy_rows([   
        'WS Fake vless',
        'WS Fake trojan',
        'WS Fake vmess',
        # 'grpc Fake vless',
        # 'grpc Fake trojan',
        # 'grpc Fake vmess',
        # "XTLS direct vless",
        # "XTLS direct trojan",
        "WS direct vless",
        "WS direct trojan",
        "WS direct vmess",
        "WS CDN vless",
        "WS CDN trojan",
        "WS CDN vmess",
        "grpc CDN vless",
        "grpc CDN trojan",
        "grpc CDN vmess",
        "tcp direct vless",
        "tcp direct trojan",
        "tcp direct vmess",
        # "h1 direct vless",
        # "h1 direct vmess",
        "faketls direct ss",
        "WS direct v2ray",
        "shadowtls direct ss",
        "tcp direct ssr",
        "WS CDN v2ray"]
    )

def make_proxy_rows(cfgs):
    
    for l3 in ["tls", "http", "kcp"]:
        for c in cfgs:
            transport,cdn,proto=c.split(" ")
            if l3=="kcp" and cdn!="direct":
                continue
            if proto=="trojan" and l3 not in ["tls",'xtls']:
                continue
            if transport in ["grpc","XTLS","faketls"] and l3=="http":
                continue


            yield Proxy(l3=l3,transport=transport,cdn=cdn,proto=proto,enable=True,name=f'{l3} {c}')