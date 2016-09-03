package com.precognizant.genpress;

import java.io.File;
import java.math.BigInteger;

import com.precognizant.genpress.Algo.Operation;

public class TestSquare {
	
	public static Algo getSquares(BigInteger num) {
		int count = 0;
		BigInteger result = num;
		System.out.println("Result = " + result);
		while(result.abs().compareTo(BigInteger.valueOf(Integer.MAX_VALUE)) > 0) {
			count++;
			result = FileUtils.sqrt(result);
		}
		System.out.println("Square = " + result + " count = " + count);
		Algo algo = new Algo();
		algo.addOperation(result.longValue(), (short)1, count * 1L);
		return algo;
	}
	
	public static void main(String[] args) throws Exception {
		File file = new File("./data/laxguys.jpg");
		if(! file.exists()) {
			throw new Exception("File does not exist: " + args[0]);
		}
 		BigInteger num = FileUtils.getFirstSegment(file).abs();
 		Algo algo = getSquares(num);
 		BigInteger clone = algo.evaluate();
 		BigInteger result = clone;
 		System.out.println("clone  = " + clone);
 		BigInteger diff = num.subtract(clone);
 		System.out.println("Diff   = " + diff);
 		BigInteger last = diff;
 		Operation op = algo.getOperation();
 		while(last.compareTo(diff) >= 0) {
 			last = diff;
 			op.first = op.first + 1;
 			result = algo.evaluate();
 	 		diff = num.subtract(result).abs();
 	 		System.out.println("Diff   = " + diff);
 		}
 		byte[] stringByte = "21094136".getBytes();
 		System.out.println("String size = " + stringByte.length);
 		byte numByte = Long.valueOf(op.first).byteValue();
 		System.out.println("numByte = " + numByte);
	}

}
