# Full-text tag review

Reviewed 24 November 2026 by an AI assistant. These are AI judgements, not labels supplied or independently validated by a human.

All 240 supplied theme assignments have a Y/N decision and an individual reason. They represent 236 distinct post texts and 236 date/text pairs. Each of 16 themes has 15 sampled assignments. The sample is from Truth Social; these results do not validate the Twitter labels.

Overall unweighted sample agreement: 176/240 = 73.3%. This measures agreement with one AI reviewer under the stated content rubric. It is not independently measured accuracy, not a human hand check, not archive-wide precision and not recall.

The review uses the supplied full text, including intelligible quoted and URL headlines. It does not fact-check claims, open linked articles or reconstruct material absent from the source export. Some original posts themselves contain ellipses.

The sample contains predicted-positive assignments only. There is no negative sample, so recall, specificity and full classifier accuracy cannot be estimated. Equal sampling by theme also means the pooled rate is not weighted to archive theme prevalence. With only 15 assignments per theme, results are approximate and sensitive to definitions.

The source rows and their order were retained, including a duplicate assignment. Do not describe 240 assignments as 240 distinct posts.

A Y means the assigned topic is meaningfully present, even if it is not the only or main topic. An N means a lexical, contextual or category-direction mismatch. The judgement is about topic meaning, not whether a post is true. borderline_definition marks calls most sensitive to theme definitions; it is not a calibrated uncertainty score.

Person-based features deserve special care: the original code intentionally includes RFK and Musk. Under this content rubric, a person-only political reference does not establish health or technology content. A broader coalition/person definition would produce different agreement rates. That is a definition issue, as well as a tagging issue.

| Theme | Y / 15 | AI agreement |

| --- | ---: | ---: |

| Economy, prices and tariffs | 5/15 | 33.3% |

| Immigration and border | 11/15 | 73.3% |

| Crime and law and order | 13/15 | 86.7% |

| Faith and values | 9/15 | 60.0% |

| Legal persecution | 13/15 | 86.7% |

| Election fraud and integrity | 10/15 | 66.7% |

| Media attacks | 10/15 | 66.7% |

| Attacks on opponents | 14/15 | 93.3% |

| Endorsing other candidates | 12/15 | 80.0% |

| Foreign policy, war and peace | 9/15 | 60.0% |

| Military and patriotism | 14/15 | 93.3% |

| Health and MAHA | 10/15 | 66.7% |

| Technology, AI and crypto | 9/15 | 60.0% |

| Sports and culture war | 13/15 | 86.7% |

| Gratitude, condolence and unity | 11/15 | 73.3% |

| Self-promotion and winning | 13/15 | 86.7% |

## Findings and impact

Economy is heavily affected by job in praise and nut jobs, and by figurative price. Faith includes Easter inside Eastern, faithfully, and faith as confidence. Foreign policy includes stock endorsement language and unrelated country references. Technology includes person-only Musk references and non-technology DOGE content. Media attacks confuse mentions, praise and criticism. These affect interpretation of coefficients; the audit alone does not quantify how much any model effect would change.

## Follow-up

Agree the intended theme definitions, independently adjudicate the decisions, then revise rules and rerun the original archives, regressions, charts and Post Checker together. A fresh holdout sample should validate the revised rules. Do not claim the existing models have already been corrected by this review.

## Rubric

- **unit**: One supplied theme/post-text assignment. Multiple themes may be meaningfully present in a post.

- **Y**: The supplied full text meaningfully contains the theme under the content definitions below. A single substantive clause or an intelligible quoted/URL headline may suffice; a theme need not dominate.

- **N**: The match is incidental, metaphorical, a generic sign-off/insult, a venue/URL-section name, a person-only reference, the wrong direction of endorsement, or otherwise not substantively on theme.

- **scope**: Judge topic meaning, not the factual accuracy of claims or whether they are agreeable. Linked articles were not opened. Full text means the text supplied in the full-text CSV; source posts may themselves contain ellipses.

- **economy_prices**: Economic conditions, employment, prices, tax, tariffs or trade. Generic job praise, nut jobs, figurative prices, unspecified bills and legal/foreign-aid monetary references alone are excluded.

- **immigration_border**: Literal immigration, migration and border policy. Wall Street Journal is excluded.

- **crime_law_order**: Domestic public safety, crime, policing, drug enforcement and security deployment. Metaphorical murder and foreign-conflict violence alone are excluded.

- **faith_values**: Religion, religious holidays/blessings, religious liberty and abortion. Eastern, faithfully, confidence in a politician and URL section names alone are excluded.

- **legal_persecution**: Trump-related court cases, prosecution, legal power or investigatory grievance. A bare agency mention or media criticism alone is insufficient.

- **election_fraud**: Election fraud/interference claims and integrity measures, including voter ID and paper/mail ballots. Fraud in unrelated litigation and the name of a case against Trump alone are excluded.

- **media_attack**: An actual criticism of a media organisation or its reporting, including social platforms. Neutral attribution, praise and favourable quotations alone are excluded.

- **attack_opponent**: An actual negative characterisation or accusation against political opponents, groups or named adversaries. A neutral mention of a Democrat alone is excluded.

- **endorsement**: Support given to another candidate or a party slate, including implicit advocacy. Self-vote appeals, endorsements received and post-election congratulations alone are excluded.

- **foreign_peace**: Foreign policy, international trade/relations, diplomacy, geopolitical conflict or peace. Domestic Russia-investigation allegations, China virus, domestic corruption allegations and generic endorsement slogans alone are excluded.

- **military_patriotic**: Actual military/defence affairs, personnel, equipment, command or associated civic policy. Metaphors and a passing institutional list alone are excluded.

- **health_maha**: Health, healthcare, diagnosis, vaccines, pandemic public-health measures and MAHA issues. RFK-only electoral/event/appointment content and pandemic voting-law context alone are excluded.

- **tech_crypto**: Technology businesses/products/use/policy, platforms, AI and crypto. Musk-only electoral/personal/DOGE staffing content or tech as a donor descriptor alone is excluded.

- **sports_culture**: Sports events/rules or substantive identity/DEI/transgender culture disputes. A golf-club venue name or generic woke insult alone is excluded.

- **gratitude_unity**: Gratitude with an audience/person/action as its object, congratulations, condolences or unity. Formulaic attention/scheduling sign-offs and great honor endorsement formulas are excluded.

- **self_promo_win**: Promotion of Trump, his products/brand/policies/claimed achievements/popularity or party electoral success. MAGA branding is included. Negative records or hostile broadcasters ratings alone are excluded.

## Provenance

https://github.com/SanketCSakhare/knox-trump-social-media-report/blob/main/outputs/hand_check_sample.csv

Source Git blob: b68989d951d3c42e322af6f3259962c66bd38f17

Source snapshot SHA-256: 79fc38549931dfa2009f1a6b793f99130406af38a92eda7409eb214f8ad9167b

The previous excerpt-based audit remains a separate historical output. These full-text decisions supersede it for this sample; its unresolved excerpt cases and mismatch counts must not be substituted for these final binary decisions.
