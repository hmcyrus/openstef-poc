/**
 * Common JavaScript utilities for DPDC OpenSTEF
 */

/**
 * Populate holiday type dropdown with options from 0 to 20
 * @param {string} selectId - The ID of the select element
 */
function populateHolidayTypeDropdown(selectId) {
    const holidayTypeOptions = [];
    for (let i = 0; i <= 20; i++) {
        holidayTypeOptions.push(`<option value="${i}" ${i === 0 ? 'selected' : ''}>${i}</option>`);
    }
    $(`#${selectId}`).html(holidayTypeOptions.join(''));
}

/**
 * Populate national event dropdown with options from 0 to 5
 * @param {string} selectId - The ID of the select element
 */
function populateNationEventDropdown(selectId) {
    const nationEventOptions = [];
    for (let i = 0; i <= 5; i++) {
        nationEventOptions.push(`<option value="${i}" ${i === 0 ? 'selected' : ''}>${i}</option>`);
    }
    $(`#${selectId}`).html(nationEventOptions.join(''));
}

/**
 * Initialize all common dropdowns (holiday_type and nation_event)
 */
function initializeCommonDropdowns() {
    populateHolidayTypeDropdown('holiday_type');
    populateNationEventDropdown('nation_event');
}

