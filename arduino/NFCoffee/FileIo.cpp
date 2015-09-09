

#include "FileIo.h"

FileIo::FileIo(){
   // On the Ethernet Shield, CS is pin 4. It's set as an output by default.
  // Note that even if it's not used as the CS pin, the hardware SS pin 
  // (10 on most Arduino boards, 53 on the Mega) must be left as an output 
  // or the SD library functions will not work. 
  pinMode(10, OUTPUT);
   if (!SD.begin(10)) {
    Serial.println("initialization failed!");
    return;
  }
  File root = SD.open("/");
  printDirectory(root,1);
    
  readFile("COFFEE.TXT");

  
}

void FileIo::printDirectory(File dir, int numTabs) {
   while(true) {
     File entry =  dir.openNextFile();
     if (! entry) {
       // no more files
       Serial.println("**nomorefiles**");
       break;
     }
     for (uint8_t i=0; i<numTabs; i++) {
       Serial.print('\t');
     }
     Serial.print(entry.name());
     if (entry.isDirectory()) {
       Serial.println("/");
       printDirectory(entry, numTabs+1);
     } else {
       // files have sizes, directories do not
       Serial.print("\t\t");
       Serial.println(entry.size(), DEC);
     }
     entry.close();
   }
}


void FileIo::readFile(char* name){
// re-open the file for reading:
  File myFile = SD.open(name);
  
  if (myFile) {
    Serial.println(name);
    
    // read from the file until there's nothing else in it:
    while (myFile.available()) {
    	Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.println("error opening File");
  }
}

//get the number of counts for a given file
int FileIo::getCount(char* filename,char* uuid){
  int retVal=-1;
  
  // re-open the file for reading:
  File myFile = SD.open(filename); 
  if (myFile) {
     char curVal='\n';
     while (myFile.available()) {
    	if(curVal=='\n'){ //newline or the first line
          byte i=0;
          for(;i<UUID_LENGTH;i++){
            char current = myFile.read();
            if(current != uuid[i]){
              break;
            }
          }
          if(i == (UUID_LENGTH)){ //A UUID match for the whole length
            char buffer[COUNT_LENGTH];
            myFile.read(); //read away the \t
            for(i=0;i<COUNT_LENGTH;i++){
              buffer[i]=myFile.read();
            }
            retVal=atoi(buffer);
            Serial.print(uuid);
            Serial.print(" - ");
            Serial.println(retVal);
            
            break;
          }
        }
        //search for new line by reading the next byte
        curVal=myFile.read(); 
    }
    // close the file:
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.println("error opening file for count");
  }
  if(retVal==-1){
    Serial.println("UUID not found");
  }
  return retVal;

}


boolean FileIo::incCount(char* filename,char* uuid){
  Serial.println("Increment Count");
  int count=getCount(filename,uuid);
  if(count < 0){ //unknown user try to create one
    if(addUuid(filename,uuid)){
      return incCount(filename,uuid);
    }else{
      return false;
    }
  }
  
  count++;
  char buffer[COUNT_LENGTH+1];
  //Buffer to Write into the FILE
  //itoa(count,buffer,10);
  sprintf(buffer,"%05d", count);
  
  //NOW Write the new Value:
   // re-open the file for reading:
  File myFile = SD.open(filename,FILE_WRITE); 
  myFile.seek(0);
  if (myFile) {
    char curVal='\n';
    while (myFile.available()) {
        
    	if(curVal=='\n'){ //newline or the first line
          byte i=0;
          for(;i<UUID_LENGTH;i++){
            if(myFile.read() != uuid[i]){
              //No Match
              break;
            }
          }
          if(i == (UUID_LENGTH)){ //A UUID match for the whole length
            myFile.read(); //read away the \t
            myFile.write(buffer);
            break;
          }
        }
        //search for new line by reading the next byte
        curVal=myFile.read(); 
    }
    // close the file:
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.println("error opening file for inc");
  }
  int now=getCount(filename,uuid);
  if(now == count ){
    return true;
  }
  
  
  return false;
}


boolean FileIo::addUuid(char* filename,char* uuid){

  File myFile = SD.open(filename,FILE_WRITE);
  if(myFile){
    myFile.write(uuid);
    myFile.write('\t');
    myFile.write("00000\n");
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.println("error opening file for inc");
    return false;
  }
  if(getCount(filename,uuid) == 0){
    return true;
  }
  
  
  return false;
}


