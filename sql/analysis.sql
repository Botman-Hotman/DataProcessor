create or replace view datawarehouse.top_related_titles as
	with target_data as (
			select 
			jt.job_title,
			count(rt.related_title) as count
			from datawarehouse.job_titles jt 
			left join datawarehouse.related_titles rt on rt.job_title = jt.job_title
			group by jt.job_title 
	)
	
	select * from target_data
	order by count desc
	limit 10;

create or replace view datawarehouse.title_pdl_count as 
	with target_data as (
			select 
			jt.job_title,
			count(rt.related_title) as count
			from datawarehouse.job_titles jt 
			left join datawarehouse.related_titles rt on rt.job_title = jt.job_title 
			group by jt.job_title 
	)
	
	select * from target_data
	order by count desc
	limit 10;

create or replace view datawarehouse.manager_titles as 
	with target_data as (
			select 
			jt.job_title,
			jt.pdl_count,
			rt.related_title
			from datawarehouse.job_titles jt 
			left join datawarehouse.related_titles rt on rt.job_title = jt.job_title 
			where rt.related_title like 'manager'
	)
	
	select 
	round(avg(pdl_count)) avg_pdl_count
	from target_data
	group by related_title;