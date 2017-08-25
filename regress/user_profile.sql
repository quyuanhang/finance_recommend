SELECT * from(
	(SELECT * from	
		(SELECT 
			id, user_id, org_id as a_oid, position,
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
			id as b_oid, prefer_industry, prefer_phase, manage_capital,
			(case when logo is null then 0 else 1 end) as logo,
			(case when website is null then 0 else 1 end) as website,
			(case when weixin is null then 0 else 1 end) as weixin,
			(case when weibo is null then 0 else 1 end) as weibo,
			(case when partner_background is null then 0 else 1 end) as partner_background,
			(case when manage_capital_currency='RMB' then 1 else 0 end) as rmb,
			(case when manage_capital_currency='USD' then 1 else 0 end) as usd,
			(case when capital_type='本土' then 1 else 0 end) as native,
			(case when capital_type='外资' then 1 else 0 end) as foreign_,
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
			from organization2) as b
		on a.a_oid = b.b_oid) as c
	inner join
	(SELECT 
		org_id as c_oid, address1 from organization_address) as c
	on a.a_oid=b.b_oid=c.c_oid

SELECT * from(
	(SELECT * from	
		(SELECT 
			id, user_id, org_id as a_oid, position,
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
			id as b_oid, prefer_industry, prefer_phase, manage_capital,
			(round(DATEDIFF(current_date(),start_date)/30)) as age_month, 
			(case when logo is null then 0 else 1 end) as logo,
			(case when website is null then 0 else 1 end) as website,
			(case when weixin is null then 0 else 1 end) as weixin,
			(case when weibo is null then 0 else 1 end) as weibo,
			(case when partner_background is null then 0 else 1 end) as partner_background,
			(case when manage_capital_currency='RMB' then 1 else 0 end) as rmb,
			(case when manage_capital_currency='USD' then 1 else 0 end) as usd,
			(case when capital_type='本土' then 1 else 0 end) as native,
			(case when capital_type='外资' then 1 else 0 end) as foreign_,
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
			from organization2) as b
		on a.a_oid = b.b_oid) as c
	inner join
	(SELECT org_id as d_oid, address1 from organization_address) as d
	on c.a_oid = d.d_oid)
	

SELECT
	id, industry1, address1, finance_phase,
	(round(DATEDIFF(current_date(),start_date)/30)) as age_month, 
	(case when logo is null then 0 else 1 end) as logo,
	(case when website is null then 0 else 1 end) as website,
	(case when scale='少于15人' then 1
				when scale='15-50人' then 2
				when scale='50-150人' then 3
				when scale='150-500人' then 4
				when scale='2000人以上' then 5
				else 0 end) as scale,
	(case when operation_status=-1 then 1 else 0 end) as pre_op,
	(case when operation_status=0 then 1 else 0 end) as op,
	(case when android_link is not null then 1 else 0 end) as android,
	(case when iphone_appstore_link is not null then 1 else 0 end) as ios,
	(case when address is not null then 1 else 0 end) as address,
	(case when telephone is not null and telephone not like '1%' then 1 else 0 end) as telephone,
	(case when telephone is not null and telephone like '1%' then 1 else 0 end) as mobile_phone,
	(case when email is not null then 1 else 0 end) as email,
	(case when weixin is null then 0 else 1 end) as weixin,
	(case when weibo is null then 0 else 1 end) as weibo,
	(case when file_business_plan is null then 0 else 1 end) as bp,
	(case when itjuzi_id is null then 0 else 1 end) as itjuzi_id,
	(case when lagou_id is null then 0 else 1 end) as lagou_id,
	(case when xiniu_id is null then 0 else 1 end) as xiniu_id,
	(case when product_and_service is null then 0 else 1 end) as product_and_service,
	(case when market_and_customer is null then 0 else 1 end) as market_and_customer,
	(case when business_model is null then 0 else 1 end) as business_model,
	(case when operation_data is null then 0 else 1 end) as operation_data,
	(case when core_resource is null then 0 else 1 end) as core_resource
FROM
company
WHERE operation_status in (-1, 0)
and finance_phase >= 0