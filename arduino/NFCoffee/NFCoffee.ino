
#include <SD.h>
#include "FileIo.h"


void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
   while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

  FileIo file;
  //Serial.println(file.getCount("COFFEE.TXT","FF01011000"));
  /*if(file.incCount("COFFEE.TXT","FF00011000")){
    Serial.println("INCREMENT");
  }
  file.incCount("COFFEE.TXT","FF01011000");
  */
  //file.incCount("COFFEE.TXT","FF000110F0");
  file.incCount("COFFEE.TXT","223446789F");

  //file.incCount("COFFEE.TXT","123456789B");
  Serial.println("done!");
}

void loop()
{
  // nothing happens after setup finishes.
}



