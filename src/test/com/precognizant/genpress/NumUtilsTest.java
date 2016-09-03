/*
 * @(#)FileUtilsTest.java $Date: Aug 18, 2016 9:50:59 PM $
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

import static org.junit.Assert.*;

import java.math.BigInteger;

import org.junit.Before;
import org.junit.Test;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Aug 18, 2016 9:50:59 PM
 */
public class NumUtilsTest {

	/**
	 * @throws java.lang.Exception
	 */
	@Before
	public void setUp() throws Exception {
	}

	/**
	 * Test method for {@link com.precognizant.genpress.FileUtils#convertToNumber(byte[])}.
	 */
	@Test
	public void testConvertToNumber() {
		//Negative
		BigInteger bi = BigInteger.valueOf(-1234567890);
		String biStr = bi.toString(2);
		System.out.println("Bi binary = " + biStr);
		byte[] buf = bi.toByteArray();
		BigInteger result = NumUtils.convertToNumber(buf);
		String resultStr = result.toString(2);
		System.out.println("Re binary = " + resultStr);
		System.out.println("Result = " + result);
		assertTrue(bi.abs().equals(result));
		
		//Large
		bi = new BigInteger("123456789012345678901234567890");
		buf = bi.toByteArray();
		result = NumUtils.convertToNumber(buf);
		System.out.println("Result = " + result);
		assertTrue(bi.equals(result));

		//Large negative
		bi = new BigInteger("-123456789012345678901234567890");
		buf = bi.toByteArray();
		result = NumUtils.convertToNumber(buf);
		System.out.println("Result = " + result);
		assertTrue(bi.equals(result));

	}

	/**
	 * Test method for {@link com.precognizant.genpress.FileUtils#sqrt(java.math.BigInteger)}.
	 */
	@Test
	public void testSqrt() {
	}

}
