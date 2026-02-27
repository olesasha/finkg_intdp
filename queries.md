# Extensions Queries

## E1: indirect impact
```cypher
MATCH (a)-[:has_positive_impact]->(b)
      -[r2:has_positive_impact]->(c)

MERGE (a)-[ind:has_positive_indirect_impact]->(c)

SET 
    ind.sector = r2.sector,
    ind.date   = r2.date,
    ind.method = 'chain_pp'

RETURN count(ind) AS updated_relationships
```

## E2: investor role

```cypher
MATCH (e)-[:invests_in]->()
SET e.role = 'investor'
RETURN count(e) AS UpdatedEntities
```

## E3: add exposure 

```cypher
MATCH (a)-[r]->(b)
WHERE type(r) IN ["invests_in", "acquires", "supplies", "controls"]
  AND r.sector IS NOT NULL
  AND r.sector <> "other"

MERGE (a)-[e:has_exposure {sector: r.sector}]->(b)
ON CREATE SET
    e.weight = 1,
    e.source = "inferred",
    e.method = "sector_exposure"
ON MATCH SET
    r.weight = coalesce(r.weight, 0) + 1
```

## E4: indirect exposure 

```cypher
 // Create indirect exposure edges
MATCH (a)-[r1:has_exposure]->(b)-[r2:has_exposure]->(c)
WHERE r2.sector IS NOT NULL AND r2.sector <> "other" AND a <> c
MERGE (a)-[e:has_indirect_exposure {sector: r2.sector}]->(c)
ON CREATE SET
    e.source = "inferred",
    e.method = "indirect_sector_exposure",
    e.weight = 1
ON MATCH SET
    e.weight = e.weight + 1
```
## E5: Remove general type "Entity"

```cypher
MATCH (n)
WHERE 'Entity' IN labels(n) AND size(labels(n)) > 1
REMOVE n:Entity
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
MATCH (:Entity)-[r:invests_in|acquires]->(target)
WHERE r.sector IS NOT NULL AND r.sector <> "other"
RETURN r.sector AS Sector,
       count(DISTINCT target) AS NumInvestmentTargets
ORDER BY NumInvestmentTargets ASC;
```

## D2: Market players with direct or indirect exposure in the chosen sector
```cypher
// Direct exposure
MATCH (e)-[r:has_exposure]->(target)
WHERE r.sector = $text_1
RETURN e AS Entity, r, target AS ExposedEntity
//LIMIT 20

UNION

// Indirect exposure
MATCH (e)-[r:has_indirect_exposure]->(target)
WHERE r.sector = $text_1
RETURN e AS Entity, r, target AS ExposedEntity
//LIMIT 20
```

## D3: Most present sectors in selected country 
```cypher
MATCH (country:Country {name: $custom})-[r]-(e)
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
MATCH (c:Country)-[r]-(e:Entity)
WHERE r.sector = $custom_1
RETURN c.name, count(c) AS NumEntities
ORDER BY NumEntities DESC
```

## D8: DisasterEvent direct impact
```cypher
// Step 1: find top connected disaster events (direct relationships only)
MATCH (c:disaster_event)-[r]->()
WHERE NOT type(r) CONTAINS "indirect"
WITH c, COUNT(r) AS relCount
ORDER BY relCount DESC
LIMIT 10

// Step 2: return all direct relationships of these top events
MATCH (c)-[r]->(e)
WHERE NOT type(r) CONTAINS "indirect"
RETURN c, r, e
LIMIT 200
```

## D9: Exposure and control per country 
```cypher
MATCH (c:Country {name: $custom})-[r]->(e)
WHERE type(r) IN ["has_exposre", "has_indirect_exposure", "controls"]
RETURN c, r, e
LIMIT $number
```

## D10: Country investments 
```cypher
MATCH (c:Country {name: $custom})-[r]->(e)
WHERE type(r) IN ["invests_in", "acquires"]
RETURN c, r, e
LIMIT $number
```

## D11: Direct impact of market players in the sector
```cypher
MATCH (e1)-[r]->(e2)
WHERE type(r) IN ["has_positive_impact",
                 "has_negative_impact"]
AND r.sector = $custom_1
RETURN e1, r, e2
LIMIT $number
```

## D12: Top 10 investors in the sector
```cypher
// Step 1: find top 10 target nodes by count
MATCH (e1)-[r]->(e2)
WHERE type(r) IN ["invests_in", "acquires"]
  AND r.sector = $custom_1
WITH e1, count(*) AS cnt
ORDER BY cnt DESC
LIMIT 10

// Step 2: get all incoming relationships for these top e2 nodes
MATCH (e1)-[r]->(e2)
WHERE type(r) IN ["invests_in", "acquires"]
  AND r.sector = $custom_1
RETURN e1, r, e2
ORDER BY e2.name  // or any other ordering
```
## D13: Investment targets and investors
```cypher
MATCH (e1)-[r]->(e2)
WHERE r.sector = $custom_1 AND type(r) IN ["invests_in", "acquires"]
WITH e2, count(*) AS cnt, collect(e1.name) AS investors
RETURN e2.name AS Target, cnt AS NumInvestments, investors
ORDER BY cnt DESC
LIMIT $number
```

## D14: Top connected entities
```cypher
MATCH (a)-[r]->(b)
WHERE NOT type(r) CONTAINS "indirect"
WITH a, b, COLLECT(r) AS rels, COUNT(r) AS NumRelationships
ORDER BY NumRelationships DESC
LIMIT 20
UNWIND rels AS r
RETURN a, b, r
```

## D15: active countries in sector 

```cypher
MATCH (country:country)-[r]-(e)
WHERE r.sector = $custom_1
  AND (r.source IS NULL OR r.source <> "inferred")
RETURN country.name AS country,
       COUNT(r) AS NumRelationships
ORDER BY NumRelationships DESC
```