/*
 * Chromosome.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.core;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.UUID;

import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Chromosome implements Runnable, Comparable<Object> {
	private ArrayList<Gene> genes;
	private Fitness fitness;
//	private BigInteger fitness = BigInteger.ZERO;
	private UUID uuid;
	private BigInteger goal = null;

	private Chromosome() {
		uuid = UUID.randomUUID();
	}
	
	public Chromosome(BigInteger goal) {
		this();
		this.goal = goal;
		genes = new ArrayList<Gene>();
		// Add genes to the chromosome until result is as big as goal
		while (goal.compareTo(this.getFitness()) == 1) {
			// Let's create a gene with the right order of magnitude
			genes.add(createGene());
		}
		this.getFitness();
	}

	private Gene createGene() {
		return new Gene(10);
	}

	public void mutate() {
		//FIXME: Change to mutate at same scale???
		Gene mutation = createGene();
		genes.set(Rand.nextInt(genes.size()), mutation);
	}

	public int getNumGenes() {
		return genes.size();
	}

	public ArrayList<Gene> getGenes() {
		return genes;
	}

	public BigInteger getFitness() {
		BigInteger result = BigInteger.ZERO;
		for(Gene gene : genes) {
			result = result.add(gene.getResult());
			//System.out.println("Gene " + gene + " Result for " + x + " " + y + " = " + result);
		}
		fitness = (Fitness) goal.subtract(result).abs();
		return (BigInteger) fitness;
	}

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	public void run() {
//		eval();
	}

	/**
	 * Used for sorting.
	 * 
	 * @see java.lang.Comparable#compareTo(java.lang.Object)
	 */
	public int compareTo(Object o) {
		if (o instanceof Chromosome) {
			Chromosome c = (Chromosome) o;
			return (this.getFitness().compareTo((BigInteger) c.fitness));
		}
		System.out.println("Chromosome.compareTo failed instanceof test. Exitting.");
		System.exit(-1);
		return 0;
	}
	
	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("\n\tUUID: " + uuid);
		buf.append("\n\tFitness: " + fitness);
		for (Gene gene : genes) {
			buf.append("\n\tGene: " + gene);
		}
		return buf.toString();
	}

	public static void main(String[] args) {
		ArrayList<Chromosome> list = new ArrayList<Chromosome>();
		for (int i = 0; i < 48; i++) {
			Chromosome c = new Chromosome(BigInteger.valueOf(13l * i));
			list.add(c);
		}
		// System.out.println("Unsorted list: " + list);
		Collections.sort(list);
		System.out.println("Sorted list: " + list);

	}

}
