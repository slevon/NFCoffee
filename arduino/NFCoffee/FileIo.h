/*
  SD card basic file example
 
 This example shows how to create and destroy an SD card file 	
 The circuit:
 * SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4
 
 created   Nov 2010
 by David A. Mellis
 modified 9 Apr 2012
 by Tom Igoe
 
 This example code is in the public domain.
 	 
 */
 
#include <Arduino.h>
#include <SD.h>

#include "main.h"



class FileIo {
  
  public:
    FileIo();
    void printDirectory(File dir, int numTabs);
    void readFile(char* name);
    int getCount(char* filename,char* uuid);
    boolean incCount(char* filename,char* uuid);
    boolean addUuid(char* filename,char* uuid);
  
};
