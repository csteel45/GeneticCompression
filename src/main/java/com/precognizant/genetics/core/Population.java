/*
 * Population.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.core;

import java.io.Serializable;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import com.precognizant.genetics.util.Rand;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 * 
 * @since Feb 15, 2011 6:28:27 PM
 */
public class Population implements Serializable {
	protected Double mutationRate = 0.4;
	private static final long serialVersionUID = 1L;
	private static final BigInteger ZERO = BigInteger.valueOf(0);
	private ArrayList<Chromosome> chromosomes;
	private int sizeMutationRate = 10 * 48; // Need to factor in number of chromosomes
	public long mutations = 0;
	private boolean elitism = true;
	private BigInteger populationFitness = BigInteger.valueOf(Long.MAX_VALUE);
	private long generation = 0;
	protected ExecutorService pool;
	private int populationSize;
	private BigInteger goal;

	public Population(BigInteger goal, int populationSize) {
		this.goal = goal;
		this.populationSize = populationSize;
		chromosomes = new ArrayList<Chromosome>(this.populationSize);
		pool = Executors.newFixedThreadPool(populationSize);
		this.setNumChromosomes(populationSize);
	}

	/**
	 * Calculates the fitness of the Population, with zero being best and higher
	 * numbers representing less fit populations.
	 * 
	 * @return BigInteger representation of fitness with 0.0 being fittest
	 */
	public BigInteger calculateFitness() {
		
		BigInteger fitness = ZERO;
		for (Chromosome c : chromosomes) {
			fitness = c.getFitness();
			if(fitness.compareTo(populationFitness) < 0) {
				System.out.println("Setting population fitness from: " + populationFitness + " to: " + fitness);
				populationFitness = fitness;
			}
		}
		sort(); // Sort the chromosomes based on fitness
		
		populationFitness = chromosomes.get(0).getFitness();
		return populationFitness;
	}
	
	public void run() {
		doCrossovers();
		calculateFitness();
		doMutations();
		calculateFitness();
		if(generation % 1000 == 1) {
			System.out.println("Fittest = " + getFittest().toString());
			//this.refactorFittest();
			//System.out.println("Refactored Fittest = " + population.getFittest().toString());
			System.out.println("Generations = " + generation + " Gene Additions = " + mutations);
		}
		generation++;

	}

	/**
	 * Performs a cross-over of Genes between Chromosomes in the Population.
	 * 
	 */
	public void doCrossovers() {
		Chromosome source = chromosomes.get(0);
		for (int i = 0; i < chromosomes.size()-1; i++) { // Iterate through all but least fit
			// Grab random genes
			int geneIndex = Rand.nextInt(source.getGenes().size());
			Gene gene = source.getGenes().get(geneIndex);
			Chromosome target = chromosomes.get(i);

			if (target.getGenes().size() >= geneIndex + 1)
				target.getGenes().set(geneIndex, gene);
			else
				target.getGenes().add(gene);
			
			if(this.elitism)
				source = chromosomes.get(i + 1); // pass crossover genes down
			else
				source = chromosomes.get(Rand.nextInt(chromosomes.size()-1)+1); // randomly crossover except to fittest
		}
	}

	public void doMutations() {
		// Let's mutate a viable percentage of the population
		int numMutations = (int) (chromosomes.size() * mutationRate);
		// System.out.println("Num mutations = " + numMutations);
		for (int i = 0; i < numMutations; i++) {
			// Grab a random Chromosome but don't mutate the fittest
			Chromosome c = chromosomes.get(Rand.nextInt(chromosomes.size() - 1) + 1);
			// Change a gene
			c.mutate();
			// Very infrequently, add a gene
			if (Rand.nextInt(sizeMutationRate) == 1) {
				mutations++;
				//System.out.println("Adding a gene. Length = " + (c.getGenes().size() + 1));
				Gene newGene = new Gene(10);
				c.getGenes().add(newGene);
				// System.out.println("adding new Gene: " + newGene);
			}
			// Or remove a gene  1/sizeMutationRate (i.e.1/10000)
			if (Rand.nextInt(sizeMutationRate) == 1) {
				if (c.getGenes().size() > 1) {
					// System.out.println("Removing a gene.");
					c.getGenes().remove(Rand.nextInt(c.getGenes().size()));
				}
			}
		}
	}

	public Chromosome getFittest() {
		sort(); // FIXME We already do a sort during calculateFitness. Can we skip it here?
		return chromosomes.get(0);
	}
	
	public void sort() {
		//System.out.println("Sort called");
		Collections.sort(chromosomes);
		//System.out.println("Most fit: " + chromosomes.get(0) + "\nLeast fit: " + chromosomes.get(chromosomes.size() - 1));
	}

	public int getNumChromosomes() {
		return chromosomes.size();
	}

	public void setNumChromosomes(int numChromosomes) {
		if (numChromosomes == chromosomes.size())
			return;

		if (chromosomes.size() < numChromosomes) {
			int diff = numChromosomes - chromosomes.size();
			for (int i = 0; i < diff; i++) {
				// Start with 1 gene per Chromosome and grow
				Chromosome c = new Chromosome(this.goal);
				chromosomes.add(c);
			}
		} 
		else {
			int diff = chromosomes.size() - numChromosomes;
			for (int i = 0; i < diff; i++) {
				chromosomes.remove(chromosomes.size() - 1);
			}
		}
		System.out.println("Population size now = " + chromosomes.size());
	}


	public Double getMutationRate() {
		return mutationRate;
	}

	public void setMutationRate(Double mutationRate) {
		this.mutationRate = mutationRate;
	}
	
	/**
	 * @param useElitism the useElitism to set
	 */
	public void setElitism(boolean elitism) {
		this.elitism = elitism;
	}

	public static void main(String[] args) {
		BigInteger goal = new BigInteger("1928374619832746891327456918327468913274591832754918327408345120394871328956109483750832410283746091827364091823468234709128347091832");
		Population population = new Population(goal, 48);
		population.run();
	}

}
