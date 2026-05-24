Feature: Goibibo train search and booking
  As a traveller
  I want to search, filter, sort, and start a train booking
  So that the booking workflow can be validated through BDD scenarios

  Background:
    Given I am on the Goibibo trains page

  @positive @filter @class
  Scenario Outline: Coach class filter shows matching train classes
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I apply coach class filter "<ClassFilterLabel>"
    Then visible train cards should show class "<ClassExpectedCode>"

    Examples:
      | Source | Destination | TravelMonth | TravelDay | ClassFilterLabel      | ClassExpectedCode |
      | ANVT   | AGC         | June        | 26        | 3A - AC 3 Tier Sleeper | 3A                |

  @positive @filter @time
  Scenario Outline: Departure time filter keeps trains inside the selected window
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I apply departure time filter "<TimeFilterLabel>"
    Then departure times should be from "<StartHour>" to before "<EndHour>"

    Examples:
      | Source | Destination | TravelMonth | TravelDay | TimeFilterLabel | StartHour | EndHour |
      | ANVT   | AGC         | June        | 26        | Afternoon       | 12        | 18      |

  @positive @filter @station
  Scenario Outline: Departure station filter shows trains from the selected station
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I apply departure station filter "<StationFilterLabel>"
    Then visible trains should depart from station code "<StationExpectedCode>"

    Examples:
      | Source | Destination | TravelMonth | TravelDay | StationFilterLabel | StationExpectedCode |
      | ANVT   | AGC         | June        | 26        | NZM - H Nizamuddin | NZM                 |

  @positive @sort @departure
  Scenario Outline: Train results can be sorted by departure time
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I sort trains by "<SortLabelKey>"
    Then trains should be sorted by departure time in ascending order

    Examples:
      | Source | Destination | TravelMonth | TravelDay | SortLabelKey |
      | ANVT   | AGC         | June        | 26        | Departure    |

  @positive @sort @arrival
  Scenario Outline: Train results can be sorted by arrival time
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I sort trains by "<SortLabelKey>"
    Then trains should be sorted by arrival time in ascending order

    Examples:
      | Source | Destination | TravelMonth | TravelDay | SortLabelKey |
      | ANVT   | AGC         | June        | 26        | Arrival      |

  @negative @booking-window
  Scenario Outline: Booking outside allowed window shows validation message
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then booking should not be open for the selected date

    Examples:
      | Source | Destination | TravelMonth | TravelDay |
      | ANVT   | AGC         | September   | 20        |

  @negative @no-trains
  Scenario Outline: Routes with no direct trains show a no trains message
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then no direct trains should be shown for "<SourceName>" to "<DestinationName>"

    Examples:
      | Source | SourceName  | Destination | DestinationName | TravelMonth | TravelDay |
      | CAPE   | Kanyakumari | BRML        | Baramula        | June        | 26        |
      | DBRG   | Dibrugarh   | BHUJ        | Bhuj            | June        | 26        |

  @regression @e2e
  Scenario Outline: Complete train booking flow reaches payment form
    When I search trains from "<Source>" to "<Destination>" on "<TravelMonth>" "<TravelDay>"
    Then train results should be displayed
    When I select an available "<ClassFilter>" train with at least "<MinAvailabilityThreshold>" seats
    And I enter IRCTC id "<IRCTCID>"
    And I add passenger "<FullName>" aged "<Age>" with gender "<Gender>" and meal "<MealOption>"
    And I enter contact mobile "<ContactMobile>" and email "<ContactEmail>"
    And I proceed to payment
    Then I should be able to fill card "<CardNumber>" expiring "<ExpiryMonth>" "<ExpiryYear>" with cvv "<CVV>" and name "<CardName>"

    Examples:
      | Source | Destination | TravelMonth | TravelDay | ClassFilter | MinAvailabilityThreshold | FullName | Age | Gender | MealOption | ContactMobile | ContactEmail       | IRCTCID       | CardNumber       | ExpiryMonth | ExpiryYear | CVV | CardName |
      | ANVT   | AGC         | June        | 26        | 2A          | 5                        | John Doe | 32  | Male   | Veg        | 9019019015    | somesome@gmail.com | priyanshu4902 | 1234567812345670 | 12          | 2030       | 123 | John Doe |
