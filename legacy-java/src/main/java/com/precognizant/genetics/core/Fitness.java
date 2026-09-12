/*
 * Fitness.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */

package com.precognizant.genetics.core;

import java.io.Serializable;

/**
 * @author Christopher Steel - Software AG Government Solutions
 *
 * @since Oct 1, 2014 11:56:12 AM
 * @version 1.0
 */
public interface Fitness extends Serializable {
	
	/**
	 * Evaluates the fitness of an individual chromosome.
	 * 
	 * @param chromosome The chromosome to evaluate
	 * @return A java.lang.Number representing the fitness. Typically, 0 will be best 
	 * and higher numbers will represent less fit chromosomes
	 */
	public Number evaluate(Chromosome chromosome);
}
