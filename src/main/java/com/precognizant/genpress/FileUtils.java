/*
 * Copyright 2016 Software AG Government Solutions
 * All Rights Reserved.
 *
 * This software is the confidential and proprietary information of Software AG
 * Government Solutions ("Confidential Information").  You shall not
 * disclose such Confidential Information and shall use it only in
 * accordance with the terms of the license agreement you entered into
 * with Software AG Government Solutions.
 *
 * SOFTWARE AG GS MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE, OR NON-INFRINGEMENT. SOFTWARE AG GS SHALL NOT BE LIABLE FOR ANY DAMAGES
 * SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
 * THIS SOFTWARE OR ITS DERIVATIVES.
 */

package com.precognizant.genpress;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;

/**
 * @author Christopher Steel - Software AG Government Solutions
 *
 * @since Mar 28, 2016 3:11:35 PM
 * @version 1.0
 */
public class FileUtils {
	private static int segmentSize = 50;
	private static int fileLength = 0;

	public static ArrayList<byte[]> parseFile(File file, int segSize) throws IOException, FileNotFoundException {
		segmentSize = segSize;
		return parseFile(file);
	}
	
	public static ArrayList<byte[]> parseFile(File file) throws IOException, FileNotFoundException {
		ArrayList<byte[]> list = new ArrayList<byte[]>();
		int lenRead = 0;
		int available = 0;
		byte[] buf = null;
		
		System.out.println("Loading file");
		FileInputStream fr = new FileInputStream(file);
		while(fr.available() > 0) {
			available = (fr.available() >= segmentSize) ? segmentSize : fr.available();
			buf = new byte[available];
			//System.out.println("Total available = " + fr.available() + " Segment available = " + available);
			lenRead = fr.read(buf, 0, available);
			fileLength += lenRead;
			//System.out.println("Lenght read: " + lenRead);
			list.add(buf);
		}
		System.out.println("Read file length: " + fileLength);
		if(lenRead != buf.length) 
			throw new IOException("File read size difference.");
		System.out.println("Loaded file");
		
		return list;
	}
	
	public static BigInteger getFirstSegment(File file) throws FileNotFoundException, IOException {
		ArrayList<byte[]> list = parseFile(file);
		byte[] first = list.get(0);
		return NumUtils.convertToNumber(first);
	}
	
	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception {
		File file = new File("./data/laxguys.jpg");
		if(! file.exists()) {
			throw new Exception("File does not exist: " + args[0]);
		}
		BigInteger val = getFirstSegment(file); 
		BigInteger orig = val;
        System.out.println("First segment number = " + val);
        int size = val.bitLength();
        System.out.println("Val size = " + size);
        int i = 0;
        while(size > 64) {
        	val = NumUtils.sqrt(val);
        	i++;
        	size = val.bitLength();
        }
        System.out.println("Sqrt val= " + val + " i = " +i + " size = " + size);
        BigInteger result = val.pow(8);
        System.out.println("Result =               " + result);
        System.out.println("Diff   =               " + orig.subtract(result));
        
	}

}
