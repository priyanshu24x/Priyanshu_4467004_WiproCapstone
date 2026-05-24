import allure
from behave import given, when, then
from selenium.webdriver.support import expected_conditions as EC

from pages.details_page import DetailsPage
from pages.homepage import HomePage
from pages.payment_page import PaymentPage
from pages.results_page import ResultsPage
from utils.logger import LogGen

logger = LogGen.loggen()


def _home(context):
    return HomePage(context.driver)


def _results(context):
    return ResultsPage(context.driver)


def _details(context):
    return DetailsPage(context.driver)


def _payment(context):
    return PaymentPage(context.driver)


@given("I am on the Goibibo trains page")
def step_open_goibibo_trains(context):
    with allure.step("Open Goibibo trains page"):
        _home(context).popup_close()
        logger.info("Goibibo train page is ready")


@when('I search trains from "{source}" to "{destination}" on "{travel_month}" "{travel_day}"')
def step_search_trains(context, source, destination, travel_month, travel_day):
    with allure.step(f"Search trains: {source} to {destination} on {travel_month} {travel_day}"):
        homepage = _home(context)
        homepage.popup_close()
        homepage.enter_source(source)
        assert source.lower() in homepage.get_selected_source_text().lower(), (
            f"Source match failure. Expected {source}, got {homepage.get_selected_source_text()}"
        )

        homepage.enter_destination(destination)
        assert destination.lower() in homepage.get_selected_destination_text().lower(), (
            f"Destination match failure. Expected {destination}, got {homepage.get_selected_destination_text()}"
        )

        homepage.select_journey_date(travel_month, travel_day)
        homepage.click_search()


@then("train results should be displayed")
def step_train_results_should_display(context):
    with allure.step("Verify train results are displayed"):
        assert _results(context).verify_results_loaded(), "Train results page failed to load"


@when('I apply coach class filter "{class_filter}"')
def step_apply_class_filter(context, class_filter):
    with allure.step(f"Apply coach class filter: {class_filter}"):
        _results(context).apply_dynamic_class_filter(class_filter)


@then('visible train cards should show class "{expected_code}"')
def step_verify_class_filter(context, expected_code):
    with allure.step(f"Verify class appears in visible train cards: {expected_code}"):
        assert _results(context).verify_class_present_in_results(expected_code), (
            f"Visible train cards did not show class {expected_code}"
        )


@when('I apply departure time filter "{time_filter}"')
def step_apply_time_filter(context, time_filter):
    with allure.step(f"Apply departure time filter: {time_filter}"):
        _results(context).apply_time_filter(time_filter)


@then('departure times should be from "{start_hour}" to before "{end_hour}"')
def step_verify_time_filter(context, start_hour, end_hour):
    with allure.step(f"Verify departure times between {start_hour} and {end_hour}"):
        assert _results(context).verify_departure_times_in_range(start_hour, end_hour), (
            f"Departure times were outside {start_hour}-{end_hour}"
        )


@when('I apply departure station filter "{station_filter}"')
def step_apply_station_filter(context, station_filter):
    with allure.step(f"Apply departure station filter: {station_filter}"):
        _results(context).apply_station_filter(station_filter)


@then('visible trains should depart from station code "{expected_code}"')
def step_verify_station_filter(context, expected_code):
    with allure.step(f"Verify departure station code: {expected_code}"):
        assert _results(context).verify_departure_station_code(expected_code), (
            f"Visible trains did not depart from {expected_code}"
        )


@when('I sort trains by "{sort_label}"')
def step_sort_trains(context, sort_label):
    with allure.step(f"Sort trains by: {sort_label}"):
        _results(context).select_sort_option(sort_label)


@then("trains should be sorted by departure time in ascending order")
def step_verify_departure_sort(context):
    with allure.step("Verify departure time ascending order"):
        assert _results(context).verify_time_sorting(check_departure=True, ascending=True), (
            "Departure times were not sorted ascending"
        )


@then("trains should be sorted by arrival time in ascending order")
def step_verify_arrival_sort(context):
    with allure.step("Verify arrival time ascending order"):
        assert _results(context).verify_time_sorting(check_departure=False, ascending=True), (
            "Arrival times were not sorted ascending"
        )


@then("booking should not be open for the selected date")
def step_verify_booking_window_error(context):
    with allure.step("Verify booking-window validation message"):
        assert _results(context).is_booking_not_open_error_shown(), (
            "Expected booking not open message was not displayed"
        )


@then('no direct trains should be shown for "{source_name}" to "{destination_name}"')
def step_verify_no_trains_message(context, source_name, destination_name):
    with allure.step(f"Verify no direct trains message for {source_name} to {destination_name}"):
        assert _results(context).is_no_trains_error_shown(), (
            f"Expected no direct trains message for {source_name} to {destination_name}"
        )


@when('I select an available "{class_filter}" train with at least "{min_seats}" seats')
def step_select_available_train(context, class_filter, min_seats):
    with allure.step(f"Select available {class_filter} train with at least {min_seats} seats"):
        results_page = _results(context)
        results_page.apply_available_only_filter()
        results_page.apply_dynamic_class_filter(class_filter)
        train_count = results_page.get_visible_train_count()
        assert train_count > 0, f"No visible trains found after applying {class_filter} filter"
        assert results_page.select_first_valid_train(class_filter, min_seats)


@when('I enter IRCTC id "{irctc_id}"')
def step_enter_irctc_id(context, irctc_id):
    with allure.step(f"Enter IRCTC id: {irctc_id}"):
        _home(context).popup_close()
        _details(context).enter_irctc_id(irctc_id)


@when('I add passenger "{name}" aged "{age}" with gender "{gender}" and meal "{meal}"')
def step_add_passenger(context, name, age, gender, meal):
    with allure.step(f"Add passenger: {name}"):
        details_page = _details(context)
        details_page.fill_passenger_details(name, age, gender, meal)
        assert details_page.is_passenger_added_successfully(name), (
            f"Passenger {name} was not added successfully"
        )


@when('I enter contact mobile "{mobile}" and email "{email}"')
def step_enter_contact(context, mobile, email):
    with allure.step(f"Enter contact details: {mobile}, {email}"):
        details_page = _details(context)
        details_page.scroll_to_element()
        details_page.select_cancellation_addon()
        details_page.wait.until(EC.visibility_of_element_located(details_page.CONTACT_NUMBER_INPUT))
        details_page.fill_contact_information(mobile, email)


@when("I proceed to payment")
def step_proceed_to_payment(context):
    with allure.step("Proceed to payment"):
        details_page = _details(context)
        details_page.wait.until(EC.element_to_be_clickable(details_page.PROCEED_TO_PAYMENT_BUTTON))
        details_page.click_proceed_to_payment()


@then('I should be able to fill card "{card_number}" expiring "{expiry_month}" "{expiry_year}" with cvv "{cvv}" and name "{card_name}"')
def step_fill_payment_card(context, card_number, expiry_month, expiry_year, cvv, card_name):
    with allure.step("Fill card details on payment page"):
        _home(context).popup_close()
        payment_page = _payment(context)
        payment_tab = payment_page.wait.until(EC.element_to_be_clickable(payment_page.CREDIT_CARD_TAB))
        assert payment_tab.is_displayed(), "Payment card tab was not displayed"
        payment_page.fill_card_details(card_number, expiry_month.zfill(2), expiry_year, cvv, card_name)
