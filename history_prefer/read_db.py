#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# 內建库

# 第三方库
import pandas as pd
# 公司开发库
sys.path.append('../../../')
import common.db_fetcher as db_fetcher

# 获取company数据
query_company = '''
SELECT * from(
    (SELECT 
        id, user_id, org_id, 
        (case when position like '%合伙人' or position like '董事%' then 1 else 0 end) as position_partner,
        (case when position like '%总裁' or position like '%总经理' then 1 else 0 end) as position_manager,
        (case when position like '%投资%' then 1 else 0 end) as position_inves,
        (case when position like '%分析师' then 1 else 0 end) as position_fa,
        (case when position like '秘书长' or position like '合伙人助理' then 1 else 0 end) as position_assistent,
        (case when intro is null then 0 ELSE 1 END) as intro,
        (case when school is null then 0 ELSE 1 END) as school,
        (case when single_invest_unit=1 or single_invest_unit=3 then 1 else 0 end) as rmb,
        (case when single_invest_unit=2 or single_invest_unit=3 then 1 else 0 end) as usd
        from investor2
        where is_36kr=0
        and is_deleted=0
        and org_type=0) as a 
    inner join
    (SELECT
        id, prefer_industry, prefer_phase, manage_capital,
        (round(DATEDIFF(current_date(),start_date)/30)) as age_month, 
        (case when logo is null then 0 else 1 end) as logo,
        (case when website is null then 0 else 1 end) as website,
        (case when weixin is null then 0 else 1 end) as weixin,
        (case when weibo is null then 0 else 1 end) as weibo,
        (case when partner_background is null then 0 else 1 end) as partner_background,
        (case when manage_capital_currency='RMB' then 1 else 0 end) as org_rmb,
        (case when manage_capital_currency='USD' then 1 else 0 end) as org_usd,
        (case when capital_type='本土' then 1 else 0 end) as native,
        (case when capital_type='外资' then 1 else 0 end) as foreig,
        (case when capital_type='合资' then 1 else 0 end) as joint,
        (case when org_type=1 or org_type=2 then 1 else 0 end) as org_is_angle,
        (case when org_type=3 or org_type=5 then 1 else 0 end) as org_is_vc,
        (case when org_type=4 or org_type=5 then 1 else 0 end) as org_is_pe,
        (case when org_type=6 then 1 else 0 end) as org_is_fofs,
        (case when org_type=7 then 1 else 0 end) as org_is_strategic,
        (case when org_type=9 then 1 else 0 end) as org_is_bank,
        (case when org_type=10 then 1 else 0 end) as org_is_fund,
        (case when org_type=11 then 1 else 0 end) as org_is_policy,
        (case when org_type=12 then 1 else 0 end) as org_is_incubator,
        (case when org_type=13 then 1 else 0 end) as org_is_fa
        from organization2) as b on a.org_id = b.id
    left join
    (SELECT org_id, address1 from organization_address) as c on a.org_id = c.org_id)
    '''



