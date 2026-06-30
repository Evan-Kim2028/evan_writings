---
title: "Data Observability with Sentio Pipelines"
date: "2024-12-01"
collection: highlights
tags:
  - writing
  - highlights
  - paragraph
source_url: https://paragraph.xyz/@evandekim/data-observability-with-sentio-pipelines
source_platform: paragraph
slug: data-observability-with-sentio-pipelines
---

***Sentio Referral Code****: Reach out to @is\_ye in the* *[sentio telegram chat](https://dune.com/evandekim/t.me/sentioxyz)* *and give the referral code evandekim2025 for a 20% discount for Sentio subscription!*

## Intro

Sentio is a game-changing development platform that enables end-to-end data observability for web3 data pipelines. The platform provides a fully integrated, hosted experience that combines modern monitoring, alerting, and debugging capabilities.

What makes Sentio particularly powerful is its real-time processing architecture: developers write and deploy typed processor code to Sentio, which automatically handles everything from historical data backfilling to real-time blockchain streaming, including automatic adjustments for chain reorganizations.

## What problems does Sentio solve?

Sentio's TypeScript pipeline interface transforms complex multi-chain development into a straightforward process, eliminating the traditional headaches of handling different blockchain protocols across multiple smart contract languages. The platform excels at:

1. Supporting diverse blockchains- EVM, SVM, MOVE, Fuel, and Starknet [(supported networks)](https://docs.sentio.xyz/docs/supported-networks)
2. Strongly typed objects for events and functions
3. Data processing, observability, and debugging wrapped up in a hosted db solution with easy sql and graphql endpoint creation for analytics
4. [Robust testing suites](https://sentioxyz.medium.com/complete-blockchain-data-testing-suites-ensure-data-reliability-and-availability-992009b60f71) for data pipelines

## Real-World Example: Sui LST Dashboard with Dune Frontend

To illustrate Sentio's capabilities, let's consider the [Sui LST Dashboard](https://dune.com/evandekim/sui-liquid-staking), a comprehensive analytics tool built using Sentio pipelines and integrated with Dune's frontend. The sentio processor code can be found [here](https://github.com/Evan-Kim2028/springsui_lsts/tree/main). This dashboard provides real-time insights into the liquid staking ecosystem on the Sui blockchain.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/15c25e53c803dd7627edf7afead02843.png)

dune lst dashboard

### **Key Features of the Sui LST Dashboard:**

* **Real-Time Data Streaming:** Continuously monitors transactions and events on the Sui network.
* **Comprehensive Analytics:** Utilizes SQL and GraphQL endpoints for detailed data queries and aggregations.
* **Seamless Integration with Dune:** Enables the creation of dynamic and interactive visualizations, making data accessible and actionable for stakeholders.

This infrastructure enables developers to quickly spin up observable data platforms that emit [pipeline metrics](https://docs.sentio.xyz/docs/metrics-in-processors), [event logs](https://docs.sentio.xyz/docs/logs-in-processor), [entities](https://docs.sentio.xyz/docs/entities), webhook and http endpoint integrations. The great thing here is that it’s all done in the background and all that’s left are for developers to use a polished product.

The integrated nature of these features creates a seamless development experience, where monitoring, debugging, and analytics all work together in real-time, making it significantly easier to build and maintain robust cross chain analytics solutions.

## Data Pipeline Process with Sentio

This section is an overview that shows an end to end flow from setting up a [Sentio processor](https://github.com/Evan-Kim2028/springsui_lsts/tree/main) with a [dune dashboard](https://dune.com/evandekim/sui-liquid-staking) as an end product. To replicate this process, simply fork the repository and add it to your own Sentio project.

### Define Sentio Processor

The main entrypoint that Sentio uses is the `processor.ts` file for instructions on how to index data. Contracts can be added with the command `yarn sentio add –chain sui_mainnet contract_address`. The abi is generally automatically fetched. Then the command `yarn sentio build` to generate the typed files. 

A processor can be defined by importing a specific class generated from the typings that contain functions. For example you can CTRL + F for `onEvent…` to find the event function bindings and click through the code to find the decoded data fields that each event holds as well. Some well prompted AI requests can make this process delightfully easy to set up multiple events from a single contract. 

### Sentio Indexing

Once the processor code has been defined, run the command `yarn sentio upload` to upload the processor code to Sentio, which will be queued up for indexing. Right out of the box, Sentio is pretty good about automatically finding the best start block point. The indexing (backfilling) process is relatively fast as well. Along the way, additional logs can be implemented into the processor to troubleshoot a data pipeline such as if there is data missing or something is not working the way it should be. These logs will appear in real time when the data gets backfilled. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/8e6577e0de457ccf7ab278521918f5bb.png)

data indexing dashboard

### Data Studio, Endpoints, and Dune

While Sentio is backfilling data, the project tables get populated in real time, so the query construction work can get started before data has finished backfilling completely. The Data Studio is where exploratory data analytics can be done and queries created for analytics such as daily aggregations, joins, and other transformations.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/5ede0503c3132a5478623bf2d67410f4.png)

data studio

After the query is ready, endpoints can be created from saved queries in 2 clicks. After the endpoint is created, the data is ready to be used outside of Sentio. In this case, Dune is used as a hosted frontend of choice. An AI connector can be used to craft Dune queries from the Sentio endpoint (see AI Prompt Miscellaneous Section).

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/d9ae316cd2bbd7f8990b40b8ca7ed010.png)

Once the data is in dune, then it can be treated as if it was any other Dune query and the dashboard can be created as usual. Note that the query has to be private to hide the Sentio API keys.

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/9e7fa21bd0c0ad730a44c0fd712d4bc3.png)

## Conclusion

Maintaining robust and observable data pipelines is paramount for the success of blockchain applications. Sentio stands out as a powerful tool for developers and data engineers, providing a seamless, integrated platform that streamlines multi-chain development and boosts real-time data observability.

By automating complex processes such as historical data backfilling and real-time blockchain streaming, Sentio not only alleviates the technical burden but also accelerates the development lifecycle. Its comprehensive feature set, including strongly typed objects and robust testing suites, empowers teams to build, monitor, and debug their data pipelines with ease and confidence. 

As blockchain technology continues to scale and diversify, data observability tools like Sentio become indispensable for ensuring that data remains reliable, accessible, and actionable.

## AI Prompt (Miscellaneous)

### **Dune LiveFetch Query Generator**

**Context:** You are using Dune's LiveFetch functions to execute SQL queries that interact with external APIs. Below is the documentation for the LiveFetch feature, followed by an example endpoint. Use this information to generate SQL queries tailored to specific API endpoints.

### **Dune LiveFetch Documentation:**

*Functions and Operators*

**LiveFetch functions**

* **Description:** LiveFetch functions send HTTP requests to a specified URL, allowing interaction with HTTP servers directly within SQL queries. They can fetch data from external APIs or invoke remote procedure calls.

**Supported Functions:**

1. `http_get(url: varchar) → varchar`
2. `http_get(url: varchar, headers: array(varchar)) → varchar`
3. `http_post(url: varchar, body: varchar) → varchar`
4. `http_post(url: varchar, body: varchar, headers: array(varchar)) → varchar`

*Additional Details:*

* **Call timeout:** 5 seconds
* **Throttling:** 50 requests per second per proxy
* **Response size limit:** 2 MiB

**Request size limit (http\_post):** 1,000,000 bytes

### *Example Endpoint:*

You have an API endpoint accessible via the following curl command:

curl -L -X POST '<https://endpoint.sentio.xyz/evandekim/sui-lst/circulating_lsts>' \

     -H 'api-key: api\_key\_here \

     -H 'Content-Type: application/json' \

     --data-raw '{}'

---

**Your Task:**

Generate a Dune SQL query using the LiveFetch functions to interact with the provided API endpoint. Ensure that all necessary headers and the request body are correctly included. If the response is in JSON format, demonstrate how to parse and extract specific fields from the response.

### **API Endpoint Details:**

* **URL:** <https://endpoint.sentio.xyz/evandekim/sui-lst/circulating_lsts>
* **Method:** POST
* **Headers:**

  + api-key: api\_key\_here
  + Content-Type: application/json
* **Body:** {}

**Requirements:**

1. Use http\_post to send the POST request.
2. Include the necessary headers.
3. Handle the JSON response to extract relevant data (e.g., list of circulating LSTs).
4. Ensure the query adheres to Dune's LiveFetch limitations.

### **Example Generated Query:**

SELECT json\_parse(

    http\_post(

        '<https://endpoint.sentio.xyz/evandekim/sui-lst/circulating_lsts>',

        '{}',

        ARRAY[

            'api-key: api\_key\_here,

            'Content-Type: application/json'

        ]

    )

) AS response\_data

To further process the JSON response, you can use Dune's JSON functions. For example:

SELECT

    json\_extract\_scalar(response\_data, '$.field\_name') AS extracted\_field

FROM (

    SELECT json\_parse(

        http\_post(

            '<https://endpoint.sentio.xyz/evandekim/sui-lst/circulating_lsts>',

            '{}',

            ARRAY[

                'api-key: api\_key\_here,

                'Content-Type: application/json'

            ]

        )

    ) AS response\_data

)

### Example Query With row extraction and filter:

WITH response AS (

    SELECT http\_post(

        '<https://endpoint.sentio.xyz/evandekim/sui-lst/circulating_lsts>',

        '{}',

        ARRAY[

            'api-key: api\_key\_here,

            'Content-Type: application/json'

        ]

    ) AS resp

),

parsed AS (

    SELECT json\_parse(resp) AS j 

    FROM response

),

rows\_array AS (

    SELECT json\_extract(j, '$.syncSqlResponse.result.rows') AS rows\_j

    FROM parsed

),

unnested\_rows AS (

    SELECT row\_data

    FROM rows\_array

    CROSS JOIN UNNEST(CAST(rows\_j AS array(json))) AS t(row\_data)

)

SELECT

    json\_extract\_scalar(row\_data, '$.event\_date') AS event\_date,

    json\_extract\_scalar(row\_data, '$.token\_name') AS token\_name,

    CAST(json\_extract\_scalar(row\_data, '$.circulating\_supply') AS double) AS circulating\_supply,

    CAST(json\_extract\_scalar(row\_data, '$.cumulative\_minted\_conv') AS double) AS cumulative\_minted,

    CAST(json\_extract\_scalar(row\_data, '$.cumulative\_redeemed\_conv') AS double) AS cumulative\_redeemed,

    CAST(json\_extract\_scalar(row\_data, '$.circulating\_supply\_usd') AS double) AS circulating\_supply\_usd,

    CAST(json\_extract\_scalar(row\_data, '$.cumulative\_minted\_usd') AS double) AS cumulative\_minted\_usd,

    CAST(json\_extract\_scalar(row\_data, '$.cumulative\_redeemed\_usd') AS double) AS cumulative\_redeemed\_usd

FROM unnested\_rows

WHERE json\_extract\_scalar(row\_data, '$.token\_name') not in ('afsui', 'vsui', 'hasui', 'springsui\_lsts', 'spring\_sui')
