package com.precognizant.genpress;

import java.math.BigInteger;
import java.util.ArrayList;

public class Algo {
	private ArrayList<Operation> operations = new ArrayList<Operation>();
	
	public Algo() {
		
	}
	
	public void addOperation(long first, short op, long second) {
		Operation operation = new Operation();
		operation.first = first;
		operation.op = op;
		operation.second = second;
		operations.add(operation);
	}
	
	public BigInteger evaluate() {
		Operation op = operations.get(0);
		BigInteger result = BigInteger.valueOf(op.first);
		for(int i = 0; i < op.second; i++) {
			result = result.multiply(result);
		}
		return result;
	}
	
	public Operation getOperation() {
		return operations.get(0);
	}
	
	public static void main(String[] args) {
		Algo algo = new Algo();
	}

	class Operation {
		long first = 0;
		short op = 1;
		long second = 0;
		
		public Operation() {
			
		}
	}
}
