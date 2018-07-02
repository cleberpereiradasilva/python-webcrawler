import os
import pyscreenshot as ImageGrab
os.environ["PATH"] += os.pathsep + r'Chrome';
from selenium import webdriver;
browser = webdriver.Chrome()
from io import BytesIO

url = 'http://www.smartredeinteligente.com.br'
browser.get(url)
#browser.set_window_size(10, 10)
img = browser.get_screenshot_as_png()
im = ImageGrab.Image.open(BytesIO(img))
pixels = im.load()
print(pixels[10,10])

field_email =       browser.find_element_by_name('email')
field_email.send_keys('usuario@empresa.com.com.br')
field_password =    browser.find_element_by_name('password')
field_password.send_keys('********')

# btn_login =    browser.find_element_by_class_name('btn')
# btn_login.click()


img = browser.get_screenshot_as_png()
im = ImageGrab.Image.open(BytesIO(img))

pixels = im.load()
print(pixels[10,10])

nova_image = im.crop((0, 0, 40, 40))
nova_image.save("vai.PNG", "PNG")

#browser.save_screenshot('page.png')
browser.quit()


retorno = driver.execute_script("document.getElementById('email').value")



#
