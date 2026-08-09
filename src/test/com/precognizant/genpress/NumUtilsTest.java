/*
 * NumUtilsTest.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
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
