/*
 * @(#)NumUtils.java $Date: Aug 22, 2016 8:43:33 PM $
 * 
 * Copyright © 2016 FortMoon Consulting, Inc. All Rights Reserved.
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

import java.math.BigInteger;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 22, 2016 8:43:33 PM
 */
public class NumUtils {

	public static BigInteger convertToNumber(byte[] buf) {
		System.out.println("Buf size = " + buf.length);
		System.out.println("OBuf = " + new BigInteger(buf).toString(2));
		//byte[] newBuf = new byte[buf.length+1];
		//newBuf[0] = 0x00000000;
		//System.arraycopy(buf, 0, newBuf, 1, buf.length);
	    BigInteger b = new BigInteger(buf);
		System.out.println("NBuf = " + b.toString(2));
//		System.out.println("BigInt =    \t" + b);
		byte[] newBuf = b.toByteArray();
		BigInteger newBi = new BigInteger(newBuf);
		System.out.println("ZBuf = " + newBi.toString(2));
		
	    return b;
	}
	
	public static BigInteger parseBigIntegerPositive(String num, int bitlen) {
	    if (bitlen < 1)
	        throw new RuntimeException("Bad bit length:" + bitlen);
	    BigInteger bref = BigInteger.ONE.shiftLeft(bitlen);
	    BigInteger b = new BigInteger(num);
	    if (b.compareTo(BigInteger.ZERO) < 0)
	        b = b.add(bref);
	    if (b.compareTo(bref) >= 0 || b.compareTo(BigInteger.ZERO) < 0 )
	        throw new RuntimeException("Out of range: " + num);
	    return b;
	}
	
	public static BigInteger sqrt(BigInteger n) {
		BigInteger a = BigInteger.ONE;
		BigInteger b = new BigInteger(n.shiftRight(5).add(new BigInteger("8")).toString());
		while (b.compareTo(a) >= 0) {
			BigInteger mid = new BigInteger(a.add(b).shiftRight(1).toString());
			if (mid.multiply(mid).compareTo(n) > 0)
				b = mid.subtract(BigInteger.ONE);
			else
				a = mid.add(BigInteger.ONE);
		}
		return a.subtract(BigInteger.ONE);
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		BigInteger bi = new BigInteger("-12312312312312312");
		byte[] buf = bi.toByteArray();
		BigInteger num = NumUtils.convertToNumber(buf);
		System.out.println("Num = " + num);
        
	}

}
