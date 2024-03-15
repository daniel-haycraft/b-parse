$Excel = New-Object -ComObject Excel.Application
 
$Workbook = $Excel.Workbooks.Open("C:\Users\Daniel Haycraft\Desktop\crossreff.xlsx")
 
$workbook.SaveAs("C:\Users\Daniel Haycraft\Desktop\crossreff.csv", 6)
 
$workbook.Close()
$Excel.Quit()

