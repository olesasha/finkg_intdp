# Extensions Queries

## E1: indirect impact
```cypher
MATCH (a:Entity)-[:has_positive_impact]->(b:Entity)
      -[r2:has_positive_impact]->(c:Entity)

MATCH (a)-[ind:has_positive_indirect_impact]->(c)

SET 
    ind.sector = r2.sector,
    ind.date   = r2.date,
    ind.method = 'chain_pp'

RETURN count(ind) AS updated_relationships
```

## E2: investor role

```cypher
MATCH (e:Entity)-[:invests_in]->(:Entity)
SET e.role = 'investor'
RETURN count(e) AS UpdatedEntities
```

## E3: add exposure 

```cypher
MATCH (a:Entity)-[r]->(b:Entity)
WHERE type(r) IN ["invests_in", "acquires", "supplies", "controls"]
  AND r.sector IS NOT NULL
  AND r.sector <> "other"

MERGE (a)-[e:has_exposure {sector: r.sector}]->(b)
ON CREATE SET
    e.weight = 1,
    e.source = "inferred",
    e.method = "sector_exposure"
ON MATCH SET
    e.weight = coalesce(e.weight, 0) + 1
```

## E4: indirect exposure 

```cypher
 // Create indirect exposure edges
MATCH (a:Entity)-[r1:has_exposure]->(b:Entity)-[r2:has_exposure]->(c:Entity)
WHERE r2.sector IS NOT NULL AND r2.sector <> "other" AND a <> c
MERGE (a)-[e:has_indirect_exposure {sector: r2.sector}]->(c)
ON CREATE SET
    e.source = "inferred",
    e.method = "indirect_sector_exposure",
    e.weight = 1
ON MATCH SET
    e.weight = e.weight + 1
```
## E5: Adding labels 
```cypher
MATCH (e:Entity)
WHERE e.type IS NOT NULL
CALL(e) {
    WITH e
    // For each possible type, add a label
    FOREACH (_ IN CASE WHEN e.type = "natural_resource" THEN [1] ELSE [] END | SET e:NaturalResource)
    FOREACH (_ IN CASE WHEN e.type = "economic_indicator" THEN [1] ELSE [] END | SET e:EconomicIndicator)
    FOREACH (_ IN CASE WHEN e.type = "industry" THEN [1] ELSE [] END | SET e:`Industry`)
}
RETURN count(e) AS UpdatedEntities
```

## E6: Remove generic labels where specific exist
```cypher
MATCH (n:Entity)
WHERE size(labels(n)) > 1
REMOVE n:Entity
RETURN n, labels(n)
LIMIT 20
```

# Dashboard queries

## F1: Filter for country custom
```cypher
MATCH (e:Country)
RETURN e.name AS Country
ORDER BY Country
```
## F2: Filter for sector custom
```cypher
MATCH ()-[r]->()
WHERE r.sector IS NOT NULL
RETURN DISTINCT r.sector AS Sector
ORDER BY Sector
```

## D1: Number of investments per sector
```cypher
MATCH (:Entity)-[r:invests_in|acquires]->(target:Entity)
WHERE r.sector IS NOT NULL AND r.sector <> "other"
RETURN r.sector AS Sector,
       count(DISTINCT target) AS NumInvestmentTargets
ORDER BY NumInvestmentTargets ASC;
```

## D2: Market players with direct or indirect exposure in the chosen sector
```cypher
// Direct exposure
MATCH (e:Entity)-[r:has_exposure]->(target:Entity)
WHERE r.sector = $text_1
RETURN e AS Entity, r, target AS ExposedEntity
//LIMIT 20

UNION

// Indirect exposure
MATCH (e:Entity)-[r:has_indirect_exposure]->(target:Entity)
WHERE r.sector = $text_1
RETURN e AS Entity, r, target AS ExposedEntity
//LIMIT 20
```

## D3: Most present sectors in selected country 
```cypher
MATCH (country:Country {name: $custom})-[r]-(e:Entity)
RETURN r.sector AS Sector, count(r) AS NumEntities
ORDER BY NumEntities DESC
```
## D4: Most influential people
```cypher
MATCH (p:Person)
MATCH (p)-[r]->()
WHERE type(r) IN [
    "has_positive_impact",
    "has_negative_impact",
    "invests_in",
    "controls",
    "acquires",
    "supplies"
]
RETURN p.name AS Person, COUNT(r) AS InfluenceScore
ORDER BY InfluenceScore DESC
LIMIT 10
```

## D5: Most influential companies
```cypher
MATCH (c)-[r]->()
WHERE ANY(lbl IN labels(c) WHERE lbl IN ["Company", "FinancialInstitution", "Regulator"])
  AND type(r) IN ["has_positive_impact", "has_negative_impact", "invests_in", "controls", "acquires", "supplies"]
RETURN c.name AS Actor,
       [lbl IN labels(c)][0] AS Type,  
       COUNT(r) AS InfluenceScore
ORDER BY InfluenceScore DESC
LIMIT 10
```
## D6: Most represented countries
```cypher
MATCH (c:Country)-[r]-()
RETURN 
    c.name AS Country,
    COUNT(r) AS NumRelationships
ORDER BY NumRelationships DESC
LIMIT 10
```
## D7: Most present countries in the sector
```cypher
MATCH (country:Country)-[r]-(e:Entity)
WHERE r.sector = $custom_1
RETURN country.name, count(country) AS NumEntities
ORDER BY NumEntities DESC
```