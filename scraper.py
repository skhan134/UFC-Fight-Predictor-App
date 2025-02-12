from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Set up Chrome driver in headless mode
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# Open the UFC athletes page
driver.get("https://www.ufc.com/athletes/all")
parsed_fighter_data = []


# While loop to click the "Load More" button
while True:
    try:
        # Locate all <li> elements with fighter info
        li_elements = driver.find_elements(By.XPATH, "//li[contains(@class, 'l-flex__item')]")

        # Wait for the "Load More" button to be clickable
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'button') and text()='Load More']"))
        )

        # Scroll to the button
        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)

        # Wait for new items to load (e.g., by checking for a new item)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'button') and text()='Load More']"))  
        )
        
        if load_more_button.is_displayed() and load_more_button.is_enabled():
            load_more_button.click()

            time.sleep(2)  # Wait for new content to load
        else:
            break # Exit loop if button is not clickable
    except Exception as e:
        print("No more items to load.")
        break

# Loop through the list of <li> elements
# Loop through the list of <li> elements
for fighter in li_elements:
    try:
        # Extract fighter data
        name = fighter.find_element(By.CLASS_NAME, 'c-listing-athlete__name').text
        division = fighter.find_element(By.CLASS_NAME, 'c-listing-athlete__title').text
        record = fighter.find_element(By.CLASS_NAME, 'c-listing-athlete__record').text

        record_numbers = record.split(" ")[0]
        wins, losses, draws = map(int, record_numbers.split("-"))

        profile_link = fighter.find_element(By.XPATH, ".//a").get_attribute("href")

        # Navigate to the fighter's profile page
        driver.get(profile_link)
        time.sleep(2)

        # Initialize variables for additional data
        striking_accuracy = None
        sig_str_landed = None
        sig_str_absorbed = None
        takedown_avg = None
        submission_avg = None
        sig_str_defense = None
        takedown_defense = None
        knockdown_avg = None
        avg_fight_time = None

        # Locate and extract additional stats
        try:
            svg_text = driver.find_element(By.CLASS_NAME, "e-chart-circle__percent")
            striking_accuracy = svg_text.get_attribute("textContent")

            # Extract Significant Strikes Landed
            sig_str_landed = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Sig. Str. Landed']]//div[@class='c-stat-compare__number']").text

            # Extract Significant Strikes Absorbed
            sig_str_absorbed = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Sig. Str. Absorbed']]//div[@class='c-stat-compare__number']").text

            # Extract Takedown Average
            takedown_avg = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Takedown avg']]//div[@class='c-stat-compare__number']").text

            # Extract Submission Average
            submission_avg = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Submission avg']]//div[@class='c-stat-compare__number']").text

            # Extract Significant Strike Defense Percentage
            sig_str_defense = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Sig. Str. Defense']]//div[@class='c-stat-compare__number']").text

            # Extract Takedown Defense Percentage
            takedown_defense = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Takedown Defense']]//div[@class='c-stat-compare__number']").text

            # Extract Knockdown Average
            knockdown_avg = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Knockdown Avg']]//div[@class='c-stat-compare__number']").text

            # Extract Average Fight Time
            avg_fight_time = driver.find_element(By.XPATH, "//div[contains(@class, 'c-stat-compare__group') and .//div[text()='Average fight time']]//div[@class='c-stat-compare__number']").text

        except Exception as e:
            # Handle cases where specific stats are not found
            print(f"Could not extract some stats for {name}: {e}")

        # Navigate back to the main page
        driver.back()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'l-flex__item')]"))
        )

        # Append the parsed data to the list
        parsed_fighter_data.append({
            "Name": name,
            "Division": division,
            "Wins": wins,
            "Losses": losses,
            "Draws": draws,
            "Striking Accuracy": striking_accuracy,
            "Sig. Str. Landed": sig_str_landed,
            "Sig. Str. Absorbed": sig_str_absorbed,
            "Takedown Avg": takedown_avg,
            "Submission Avg": submission_avg,
            "Sig. Str. Defense": sig_str_defense,
            "Takedown Defense": takedown_defense,
            "Knockdown Avg": knockdown_avg,
            "Average Fight Time": avg_fight_time
        })

    except Exception as e:
        # Handle cases where a fighter's data could not be fully parsed
        print(f"Error parsing data for a fighter: {e}")

# Create and save DataFrame
df = pd.DataFrame(parsed_fighter_data)
# Ensure no unsupported types
df['Wins'] = df['Wins'].astype(int)
df['Losses'] = df['Losses'].astype(int)
df['Draws'] = df['Draws'].astype(int)

# Clean column names (replace spaces with underscores)
df.columns = df.columns.str.replace(' ', '_')

# Optionally, handle missing values
df.fillna('', inplace=True)

df.to_csv("fighter_records.csv", index=False)

# Close the browser
driver.quit()