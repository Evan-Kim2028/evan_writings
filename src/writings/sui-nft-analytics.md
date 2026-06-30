---
title: "Sui NFT Analytics"
date: "2025-02-01"
collection: highlights
tags:
  - writing
  - highlights
  - paragraph
source_url: https://paragraph.xyz/@evandekim/sui-nft-collection-analytics
source_platform: paragraph
slug: sui-nft-analytics
---

# Intro

This article presents a framework for building data pipelines on the Sui blockchain using Sentio, illustrated through a complete implementation to analyze Rootlets NFT holders. Sentio is used for efficient data backfilling, custom processing with TypeScript, and real-time analysis via its SQL Studio. The article culminates in demonstrating a user-friendly Sentio [dashboard](https://app.sentio.xyz/share/gzpkjey8llpnam4y?from=now-30d&to=now) that queries Rootlet ownership by wallet address. This approach provides a reusable and adaptable foundation for developing data-driven applications and insights across the Sui ecosystem.

# Sentio Processor Pipeline

[Sentio processors](https://docs.sentio.xyz/docs/processor-basic), written in TypeScript, provide a flexible way to construct Sui data pipelines. They manage the essential ETL (Extract, Transform, Load) steps for interacting with Sui blockchain data. 

Processors define how data is extracted, transformed (including handling Sui-specific features like object ownership), and loaded into Sentio's database. They serve as the central logic for data processing, ensuring only relevant and correctly structured data is stored for analysis. The complete processor code for this article is available [here](https://github.com/Evan-Kim2028/rootlets).

## Defining Entities

[Entities](https://docs.sentio.xyz/docs/entities) in Sentio are analogous to custom tables, structuring data for optimized analysis. Entities are defined in a store.graphql file, located at src/schema/store.graphql. This file uses a GraphQL-like syntax to describe the structure of our custom tables.

For the Rootlets project, there are two main entities:

* **RootletStaticFields**: This entity captures the static fields of a Rootlet object, such as its description, image URL, and inherent traits (theme, accessories, etc.). This is information that doesn't change over time.
* **RootletOwner**: This entity tracks changes in Rootlet ownership. Every time a Rootlet is transferred or modified, a new entry is created in this entity, recording the sender, transaction digest, and timestamp. This is crucial for tracking who owns which Rootlets over time.

## Generating Bindings

After defining entities in src/schema/store.graphql, the command [yarn sentio build](https://docs.sentio.xyz/docs/cli-reference#sentio-build) generates TypeScript code. This generated code facilitates interaction with these entities within the processor, enabling the creation and updating of records during data processing.

# SQL Query Analytics

Sentio provides a built-in SQL Studio, a web-based interface where you can write and execute SQL queries against your data. As the backfilling process populates your entities (which now appear as tables), you can start writing SQL queries to analyze the data in real-time.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/61e7c8d2e76fb5178d1d7fad21df732e.png)

## Rootlet Holder Count Growth

A unique holder count growth over time can be constructed using the RootletOwner table. This query is crucial for taking arbitrary historical snapshots of Rootlet ownership.

Sui NFT objects are stored either in kiosks or as wrapped objects, resulting in the true owner often being a nested object value. Instead of recursive searching for the true owner, the sender address is used. Sui's consensus mechanism performs a runtime validation check, ensuring that the object mutator is already the object's owner. Therefore, if the object is mutated, it is assumed that the mutation was performed by the owner. This principle allows the storage of ownership history in a table, tracking the transaction sender each time the object is mutated.

Here is what the chart looks like in the Sentio dashboard:

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/6a52108480404c0269a7ae083d65d251.png)

The full query is available in the Appendix.

## Rootlet Holder Count Growth

A second query categorizes Rootlet owners qualitatively (see Appendix for the query). This query joins the theme value, a static object value stored in RootletStaticFields, to the latest owner from RootletOwner.

This dashboard integration demonstrates the flexibility of the Sentio data pipeline. Not only can queries provide aggregate statistics, but they also enable detailed, address-specific analysis, such as determining the exact Rootlet holdings of an address Moreover, this level of data granularity enables targeted airdrops, for example, rewarding holders based on specific Rootlet attributes or ownership history.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/31875b43952708e9c3726fa11636bf61.png)

## Conclusion

This article presented a comprehensive guide to building a Sui data pipeline for the Rootlets NFT collection using Sentio. The process began with defining custom entities to structure the data, followed by utilizing Sentio's TypeScript processors to handle data extraction, transformation, and the specific challenges of Sui object ownership. The integrated SQL Studio was then used to perform real-time analysis, generating queries for key metrics like holder count growth and thematic categorization. 

The culminating dashboard, parameterized by wallet address, demonstrates the power of this pipeline for in-depth analysis. This approach not only provides valuable insights into the Rootlets collection but also establishes a reusable framework for developing more sophisticated data pipelines and analytical tools within the Sui ecosystem.

## SQL Query Appendix

### Rootlet Holder Count Growth

```
WITH OrderedEvents AS (

   SELECT

       ro1.objectID,

       ro1.sender,

       toDate(ro1.timestamp / 1000) AS start_date,

       ifNull(argMin(toDate(ro2.timestamp / 1000), ro2.timestamp), toDate('2106-02-07')) AS end_date

   FROM RootletOwner ro1

   LEFT JOIN RootletOwner ro2

   ON ro1.objectID = ro2.objectID AND ro1.timestamp < ro2.timestamp

   GROUP BY ro1.objectID, ro1.sender, ro1.timestamp

),

-- Convert dates to integers for range function

DateRanges AS (

   SELECT

       objectID,

       sender,

       toUInt32(start_date) AS start_date_int,

       toUInt32(end_date) AS end_date_int

   FROM OrderedEvents

),

-- Expand date ranges into individual dates

ExpandedDates AS (

   SELECT

       objectID,

       sender,

       toDate(start_date_int + number) AS day

   FROM DateRanges

   ARRAY JOIN range(0, end_date_int - start_date_int) AS number

),

-- Get all distinct dates

AllDates AS (

   SELECT DISTINCT toDate(timestamp / 1000) AS day

   FROM RootletOwner

)

-- Join expanded dates with all dates and count distinct senders

SELECT

   ad.day,

   count(DISTINCT ed.sender) AS unique_holder_count

FROM AllDates ad

LEFT JOIN ExpandedDates ed ON ad.day = ed.day

GROUP BY ad.day

ORDER BY ad.day;
```

### Rootlet Holder Count Per Theme

```
WITH LatestOwners AS (

   SELECT

       objectID,

       argMax(sender, timestamp) AS latest_sender

   FROM RootletOwner

   GROUP BY objectID

)

SELECT

   lo.latest_sender,

   s.theme,

   COUNT() AS theme_count

FROM LatestOwners AS lo

INNER JOIN RootletStaticFields AS s ON lo.objectID = s.id

GROUP BY lo.latest_sender, s.theme

ORDER BY theme_count DESC
```
