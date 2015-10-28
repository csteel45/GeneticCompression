/*
 * @(#)Compress.java $Date: Sep 7, 2015 3:17:07 PM $
 * 
 * Copyright © 2015 FortMoon Consulting, Inc. All Rights Reserved.
 * 
 * This software is the confidential and proprietary information of FortMoon
 * Consulting, Inc. ("Confidential Information"). You shall not disclose such
 * Confidential Information and shall use it only in accordance with the terms
 * of the license agreement you entered into with FortMoon Consulting.
 * 
 * FORTMOON MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
 * SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
 * NON-INFRINGEMENT. FORTMOON SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY
 * LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES.
 * 
 */
package com.precognizant.genpress;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.util.ArrayList;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Sep 7, 2015 3:17:07 PM
 */
public class Compress {
	
	private int segmentSize = 5000;
	private int fileLength = 0;

	public Compress() {	
	}
	
	public BigInteger convertToNumber(byte[] buf) {
		BigInteger num = null;
		num = new BigInteger(buf);

		return num;
	}
	
	public byte[] convertToBytes(BigInteger num, byte start) {
		// Copy away the first byte which was used to represent sign. Don't modify, this works.
		byte[] buf = num.toByteArray();
		byte[] out = new byte[buf.length + 1];
		out[0] = start;
		System.arraycopy(buf, 0, out, 1, buf.length);
		return out;
	}
	
	public ArrayList<byte[]> parseFile(File file) throws IOException, FileNotFoundException {
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
	
	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception {
		Compress comp = new Compress();
		
		File file = new File("./data/laxguys.jpg");
		if(! file.exists()) {
			throw new Exception("File does not exist: " + args[0]);
		}
		
		ArrayList<byte[]> list = comp.parseFile(file);
		System.out.println("Divided file into a number of 5000 byte segments = " + list.size());
		// HERE WE DO THE WORK
		// Let's play with just the first
		System.out.println("Grabbing first segment of size = " + list.get(0).length);
		byte[] first = list.get(0);
		BigInteger firstNum = comp.convertToNumber(first);
		System.out.println("First number byte count = " + firstNum.bitLength()/8);
		BigInteger squared = firstNum.multiply(firstNum);
		System.out.println("First number squared byte count = " + squared.bitLength()/8);
		BigInteger powered = firstNum.pow(100);
		System.out.println("First number power of int max  = " + powered.bitLength()/8);
		
		ByteBuffer bb = ByteBuffer.allocate(comp.fileLength);
		for(int i = 0; i < list.size(); i++) {
			bb.put(list.get(i));
		}
		byte[] buf = bb.array();
		BigInteger num = comp.convertToNumber(buf);
		
		byte[] obuf = comp.convertToBytes(num, buf[0]);
		System.out.println("Converted num to buf length: " + obuf.length);
		for(int i = 0; i < buf.length; i++) {
			if(buf[i] != obuf[i])
				throw new Exception("Bytes do not match at: " + i + " buf = " + buf[i] + " obuf = " + obuf[i]);
		}
		File out = new File("data/out.jpg");
		FileOutputStream os = new FileOutputStream(out);
		os.write(obuf);
		os.flush();
		os.close();

		int byteSize = 5000;
		int length = 0;
		int pow = 1000;
		
		while(length < byteSize) {
			length = (BigInteger.valueOf(10).pow(pow)).bitLength();
			pow += 1;
			//System.out.println("Pow = " + pow + " length = " + length);
		}
		System.out.println("Pow = " + pow + " length = " + length);
	}

}
