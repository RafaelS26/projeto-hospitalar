use hospitalDB;


select top 10 * from pacientes;

-- média de deposito por tipo de hospital
select  top 10  Hospital_type_code, avg (deposito) as média_deposito
from pacientes 
group by Hospital_type_code;

-- Qual Hospital tem mais pacientes ?
select Hospital_code , count (*) as total_pacientes 
from pacientes  
group by Hospital_code 
order by total_pacientes desc;


-- Qaul Hospital tem o maior valor de agregado ?
select Hospital_code , sum (deposito) as valor_total_deposito, avg (deposito) as média_por_pacientes
from pacientes  
group by Hospital_code 
order by valor_total_deposito desc;

-- Qual o perfil de gravidade por tipo de adimissão?

select tipo_admissao ,Severity_of_Illness , count (*) as Quantidades
from pacientes 
group by tipo_admissao , Severity_of_Illness
order by tipo_admissao, Quantidades desc;


-- Visão Geral: Idade Média e Deposito Médio 
select avg (idade) as idade_media, avg (deposito) as deposito_medio, 
min (idade) as idade_minima, max (idade) as idade_maxima
from pacientes;

------------------------ Top Performace -----------------


select * from pacientes;


SELECT 
    department, 
    COUNT(*) AS total_pacientes,
    ROUND(AVG(deposito), 2) AS deposito_medio,
    ROUND(Sum(deposito) , 2) AS valor_total_retido
FROM pacientes
GROUP BY department
ORDER BY valor_total_retido DESC


SELECT 
    department,
    COUNT(*) AS total_pacientes,
    -- Agora usando o número 2 para casos extremos
    SUM(CASE WHEN Severity_of_Illness = '2' THEN 1 ELSE 0 END) AS casos_extremos,
    -- Calculando o percentual corretamente
    ROUND(SUM(CASE WHEN Severity_of_Illness = '2' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_casos_extremos,
    ROUND(AVG(deposito), 2) AS deposito_medio
FROM pacientes
WHERE department <> 'Department' -- Tirando o lixo do cabeçalho
GROUP BY department
ORDER BY total_pacientes DESC;


-----------------------------------------------------------
-------------------Comportamento do hospital---------------
-- Departamento Segura  o paciente por mais tempo ? 
select department,
       avg (case
            when stay = '0-10' then 5
            when stay = '11-20' then 15
            else 30 end ) as média_permanencia_estimada 
from pacientes
group by department;


SELECT 
    department,
    COUNT(*) AS total_pacientes,
    ROUND(AVG(deposito), 2) AS deposito_medio,
    
    -- CÓDIGO LIMPO: Transformando a conta em DECIMAL para sumir com os zeros
    CAST(
        ROUND(SUM(CASE WHEN Severity_of_Illness = '2' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) 
    AS DECIMAL(10,2)) AS pct_casos_extremos,
    
    ROUND(AVG(CAST(Visitors_with_Patient AS INT)), 1) AS media_visitantes
FROM pacientes
WHERE department <> 'Department'
GROUP BY department
HAVING COUNT(*) > 20
ORDER BY pct_casos_extremos DESC;


