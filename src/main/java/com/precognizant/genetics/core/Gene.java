/*
 * @(#)Gene.java $Date: Feb 15, 2011 6:28:27 PM $
 * 
 * Copyright 2011 FortMoon Consulting, Inc. All Rights Reserved.
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
package com.precognizant.genetics.core;

import java.io.File;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;
import java.util.ArrayList;

import com.precognizant.genetics.operand.MathOperand;
import com.precognizant.genpress.Compress;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Gene {
	private BigInteger result = BigInteger.ZERO;
	private MathOperand operand;
	
	public Gene(int scale) {
		BigInteger param1 =  BigInteger.valueOf((long)Math.pow(Math.random()*10.0, 100.0));
		BigInteger param2 = BigInteger.valueOf((long)(Math.random()*1000.0));
		operand = new MathOperand(MathOperand.Operation.POWER);
		System.out.println("Param 1 = " + param1 + " Param 2 = " + param2);
		result = operand.evaluate(param1, param2);
	}
	
	public String toString() {
		return this.toString();
	}
	
	/**
	 * Used for sorting.
	 * 
	 * @see java.lang.Comparable#compareTo(java.lang.Object)
	 */
	public int compareTo(Object o) {
		if (o instanceof Gene) {
			Gene gene = (Gene) o;
			return (this.getResult().compareTo(gene.getResult()));
		}
		System.out.println("Gene.compareTo failed instanceof test. Exitting.");
		System.exit(-1);
		return 0;
	}

	/**
	 * @return
	 */
	public BigInteger getResult() {
		return result;
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
		BigInteger result = a.subtract(BigInteger.ONE);
		System.out.println("Squared  : " + result);
		return result;
	}
	
	private static final BigDecimal SQRT_DIG = new BigDecimal(1000);
	private static final BigDecimal SQRT_PRE = new BigDecimal(10).pow(SQRT_DIG.intValue());

	/**
	 * Private utility method used to compute the square root of a BigDecimal.
	 * 
	 * @author Luciano Culacciatti 
	 * @url http://www.codeproject.com/Tips/257031/Implementing-SqrtRoot-in-BigDecimal
	 */
	private static BigDecimal sqrtNewtonRaphson  (BigDecimal c, BigDecimal xn, BigDecimal precision){
	    BigDecimal fx = xn.pow(2).add(c.negate());
	    BigDecimal fpx = xn.multiply(new BigDecimal(2));
	    BigDecimal xn1 = fx.divide(fpx,2*SQRT_DIG.intValue(),RoundingMode.HALF_DOWN);
	    xn1 = xn.add(xn1.negate());
	    BigDecimal currentSquare = xn1.pow(2);
	    BigDecimal currentPrecision = currentSquare.subtract(c);
	    currentPrecision = currentPrecision.abs();
	    if (currentPrecision.compareTo(precision) <= -1){
	        return xn1;
	    }
	    return sqrtNewtonRaphson(c, xn1, precision);
	}

	/**
	 * Uses Newton Raphson to compute the square root of a BigDecimal.
	 * 
	 * @author Luciano Culacciatti 
	 * @url http://www.codeproject.com/Tips/257031/Implementing-SqrtRoot-in-BigDecimal
	 */
	public static BigDecimal bigSqrt(BigDecimal c){
	    return sqrtNewtonRaphson(c,new BigDecimal(1),new BigDecimal(1).divide(SQRT_PRE));
	}
	
	public static void main(String[] args) throws Exception {
		double x = 0.7;
		int y = (int)x;
		int a = 14;
		double b = a;
		System.out.println("\\* This is not\n a comment *\\");
		double answer =  (double) (13 / 5);
		System.out.println("Answer = " + answer);
		int result1 = 13 - 3 * 6 / 4 % 3;
		System.out.println("Result1 = " + result1);
		int result2 = (2 + 3) * 12 / (7 -4 + 8);
		System.out.println("Result2 = " + result2);
		x = 0.0;
		while(((Math.pow(x, 0.5)) == Math.sqrt(x))) {
			x++;
		}
		System.out.println("POW = " + ((Math.pow(x, 0.5)) == Math.sqrt(x)) + " for x = " + x);
		
		int n = 0;
		if(n != 0 && x /n > 100) {
			System.out.println("Hi");
		}
		else {
			System.out.println("Bye");
		}
		
		int num = 22;
		if(num > 0)
			if(num % 5 == 0)
				System.out.println(num);
			else System.out.println(num + " is negative");
		
		
		BigInteger test = BigInteger.valueOf(5).pow(17000);
		System.out.println("Test scale: " + test.bitLength()/8);
		File file = new File("./data/laxguys.jpg");
		if(! file.exists()) {
			throw new Exception("File does not exist: " + args[0]);
		}
		Compress comp = new Compress();
		ArrayList<byte[]> list = comp.parseFile(file);
		System.out.println("Divided file into a number of 500 byte segments = " + list.size());
		// HERE WE DO THE WORK
		// Let's play with just the first
		System.out.println("Grabbing first segment of size = " + list.get(0).length);
		byte[] first = list.get(0);
		BigInteger segment = comp.convertToNumber(first);
		BigDecimal square = new BigDecimal(segment);
		
//		BigInteger square = sqrt(segment);
		ArrayList<BigInteger> squareList = new ArrayList<BigInteger>();
		int count = 0;
		BigDecimal temp = square;
		int counter = 0;
		while(square.compareTo(new BigDecimal(Long.MAX_VALUE)) == 1) {
			square = bigSqrt(temp);
			BigDecimal fracBd = square.subtract(new BigDecimal(square.toBigInteger()));
			System.out.println("Remainder: " + fracBd);
			//System.out.println("Found a rounded square after: " + counter);
			//System.exit(0);
			square = bigSqrt(square);
			squareList.add(square.toBigInteger());
			count++;
		}
		System.out.println("Final square = " + square + " count = " + count);
		BigInteger build = square.toBigInteger();
		for(int i = 0; i < count; i++) {
			//System.out.println("Squaring : " + build);
			BigInteger tmpSquare = squareList.get((squareList.size()-1) - i);
			BigInteger difference = tmpSquare.subtract(build);
			System.out.println("tmpSquare  = " + tmpSquare);
			System.out.println("build      = " + build);
			System.out.println("Difference = " + tmpSquare.subtract(build));
			build = build.add(difference); // Add on difference
			build = build.multiply(build);
		}
		System.out.println("Build diff = " + segment.subtract(build));
		System.out.println("Build count = " + segment.bitLength()/8);
		
		System.out.println("Segment = " + segment);
		System.out.println("Segment byte count = " + segment.bitLength()/8);

		int goalScale = segment.bitLength()/8;
		int scale = goalScale;
		System.out.println("Goal scale: " + goalScale);
		Gene gene = new Gene(goalScale);
		BigInteger result = gene.getResult();
	}
}
