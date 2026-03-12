# Contributing to Llamaball

Thank you for your interest in contributing to Llamaball! This guide will help you get started.

## 🎯 Project Philosophy

Llamaball is built with **performance optimization and local privacy** as core principles. All contributions should align with these values:

- **Performance First**: Every feature must maintain sub-second response times and optimal resource usage
- **Local Privacy**: All processing happens locally, no data leaves the user's machine
- **Developer-Friendly**: Code should be self-documenting with comprehensive type hints and performance considerations
- **Scalability**: Support for large datasets with efficient memory management and parallel processing

## 🚀 Quick Start

### Development Setup

```bash
# Clone the repository with submodules
git clone --recursive https://github.com/coolhand/llamaball.git
cd llamaball

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e .[dev,test,docs,performance]

# Install pre-commit hooks for code quality
pre-commit install

# Setup development environment with profiling tools
python -m llamaball setup-dev --all
```

### Running Tests & Benchmarks

```bash
# Run all tests with coverage
pytest --cov=llamaball --cov-report=html --cov-report=term

# Run performance benchmarks
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

# Run specific test file with profiling
pytest tests/test_core.py -v --profile

# Memory profiling
python -m memory_profiler scripts/memory_test.py

# Benchmark embedding generation
python benchmarks/embedding_benchmark.py --models all --datasets test
```

### Code Quality & Performance

```bash
# Format code
black llamaball/ tests/
isort llamaball/ tests/ --profile black

# Type checking with strict mode
mypy llamaball/ --strict --show-error-codes

# Linting
flake8 llamaball/ tests/ --max-line-length 88

# Security analysis
bandit -r llamaball/ -f json -o security-report.json

# Run all quality checks
pre-commit run --all-files

# Performance profiling
python -m cProfile -o profile.stats -m llamaball chat --profile
```

## 📝 Development Guidelines

### Code Style & Performance

- **Python Version**: Support Python 3.8+, optimized for 3.11+
- **Formatting**: Use `black` with 88-character line length
- **Import Sorting**: Use `isort` with black profile
- **Type Hints**: All functions must have comprehensive type hints
- **Docstrings**: Use Google-style docstrings with performance notes
- **Performance**: Include complexity analysis and optimization considerations
- **Memory Management**: Efficient resource usage and cleanup
- **Error Handling**: Graceful degradation with performance fallbacks

### Performance Requirements

1. **Speed Optimization**: Sub-second response times for all operations
2. **Memory Efficiency**: Minimal RAM usage with intelligent caching
3. **Scalability**: Support for large datasets (100k+ documents)
4. **Parallel Processing**: Multi-threaded operations where beneficial
5. **Resource Monitoring**: Built-in profiling and performance metrics

### Documentation Standards

```python
def example_function(param: str, batch_size: int = 32, parallel: bool = True) -> dict:
    """High-performance document processing with optimization.
    
    Processes documents in parallel batches for optimal throughput.
    Time complexity: O(n/p) where n=documents, p=parallel workers.
    Memory usage: O(batch_size * avg_doc_size).
    
    Args:
        param: Input parameter for processing
        batch_size: Number of documents to process in parallel (default: 32)
        parallel: Enable multi-threaded processing for performance
        
    Returns:
        Dictionary containing results with performance metrics
        
    Raises:
        ValueError: When param is invalid
        MemoryError: When batch_size exceeds available memory
        
    Performance:
        - Typical throughput: 500-2000 docs/minute
        - Memory usage: ~100MB per 1000 documents
        - Scales linearly with worker count
    """
    pass
```

## 🔧 Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/performance-optimization
# or
git checkout -b fix/memory-leak-issue
```

### 2. Make Your Changes

- Write code following performance guidelines above
- Add comprehensive tests including performance benchmarks
- Update documentation with performance implications
- Include profiling data for significant changes
- Ensure memory efficiency and proper resource cleanup

### 3. Test Your Changes

```bash
# Run comprehensive test suite
pytest --cov=llamaball --benchmark-only

# Test CLI functionality with profiling
llamaball --help
llamaball ingest test_data/ --workers 8 --profile
llamaball chat --debug --show-performance

# Performance regression testing
python scripts/performance_regression.py

# Memory leak detection
python scripts/memory_leak_test.py
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message including performance impact
git commit -m "feat: optimize embedding generation with 40% speed improvement"

# Push to your branch
git push origin feature/performance-optimization
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) with performance focus:

- `feat:` - New features (include performance impact)
- `fix:` - Bug fixes (mention performance implications)
- `perf:` - Performance improvements
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring (note performance changes)
- `test:` - Adding or updating tests (include benchmarks)
- `chore:` - Maintenance tasks

### Performance-Focused Commit Examples

```bash
git commit -m "perf: optimize vector search with 60% latency reduction"
git commit -m "feat: add async processing support for 10x throughput"
git commit -m "fix: resolve memory leak in embedding cache (saves 200MB)"
```

## 🐛 Reporting Issues

### Performance Issues

When reporting performance problems, please include:

1. **Environment**: OS, Python version, Ollama version, hardware specs
2. **Performance Metrics**: Response times, memory usage, CPU utilization
3. **Dataset Size**: Number and size of documents processed
4. **Steps to Reproduce**: Clear, numbered steps with timing information
5. **Expected Performance**: What performance you expected
6. **Actual Performance**: Measured performance with metrics
7. **Profiling Data**: Include cProfile or memory_profiler output if available

### Bug Reports

For general bugs, include:

1. **Environment**: Complete system information
2. **Steps to Reproduce**: Clear, numbered steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happened
5. **Error Messages**: Full error output with stack traces
6. **Performance Impact**: Does this affect system performance?

### Feature Requests

For feature requests, please describe:

1. **Use Case**: Why is this feature needed?
2. **Performance Requirements**: Expected throughput, latency, memory usage
3. **Scalability Needs**: How should this perform with large datasets?
4. **Privacy Impact**: Does this maintain local-only processing?
5. **Proposed Implementation**: Ideas for efficient implementation
6. **Performance Benchmarks**: How will we measure success?

## 📊 Performance Testing

### Benchmark Categories

1. **Document Processing**: Ingestion speed, chunking efficiency
2. **Embedding Generation**: Throughput, memory usage
3. **Search Performance**: Query latency, result relevance
4. **Memory Management**: Usage patterns, garbage collection
5. **Concurrent Operations**: Multi-user scenarios, resource contention

### Performance Standards

- **Document Ingestion**: 500+ documents/minute
- **Search Latency**: <50ms for 10k documents
- **Memory Efficiency**: <500MB RAM for 10k documents
- **Embedding Generation**: 50+ embeddings/second
- **Startup Time**: <2 seconds for CLI initialization

### Profiling Tools

```bash
# CPU profiling
python -m cProfile -o profile.stats script.py

# Memory profiling
python -m memory_profiler script.py

# Line-by-line profiling
kernprof -l -v script.py

# Memory usage over time
mprof run script.py
mprof plot
```

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create** a performance-focused branch
3. **Make** your changes following the performance guidelines
4. **Test** thoroughly including performance benchmarks
5. **Submit** a pull request with:
   - Clear description of changes and performance impact
   - Reference to related issues
   - Performance benchmarking results
   - Memory usage analysis
   - Profiling data for significant changes

### Pull Request Template

```markdown
## Description
Brief description of changes and performance improvements

## Type of Change
- [ ] Bug fix (include performance impact)
- [ ] New feature (include performance benchmarks)
- [ ] Performance optimization
- [ ] Documentation update
- [ ] Refactoring (note performance changes)

## Performance Impact
- [ ] Faster execution (include metrics)
- [ ] Lower memory usage (include measurements)
- [ ] Better scalability (include test results)
- [ ] No performance change

## Testing
- [ ] Tests pass
- [ ] Performance benchmarks completed
- [ ] Memory profiling completed
- [ ] Regression testing completed

## Performance Checklist
- [ ] Sub-second response times maintained
- [ ] Memory usage optimized
- [ ] Scalability tested with large datasets
- [ ] Resource cleanup implemented
- [ ] Error handling with performance fallbacks

## Benchmarks
Include before/after performance metrics:
- Response time: X ms → Y ms (Z% improvement)
- Memory usage: X MB → Y MB (Z% reduction)
- Throughput: X ops/sec → Y ops/sec (Z% increase)

## Documentation
- [ ] Docstrings updated with performance notes
- [ ] README updated if needed
- [ ] CHANGELOG updated with performance improvements
- [ ] Performance guide updated
```

## 🏆 Recognition

Contributors will be recognized in:

- README.md acknowledgments with performance contributions highlighted
- CHANGELOG.md for significant performance improvements
- GitHub contributors list
- Performance leaderboard for optimization contributions

## 📞 Getting Help

- **Issues**: Open a GitHub issue for bugs or performance questions
- **Discussions**: Use GitHub Discussions for architecture and optimization topics
- **Performance Forum**: Dedicated section for performance optimization discussions
- **Email**: Contact maintainers for security or critical performance issues

## 📊 Development Tools

### Recommended IDE Setup

- **VSCode**: Python extension with performance profiler integration
- **PyCharm Professional**: Built-in profiler and memory analysis
- **Vim/Neovim**: With performance monitoring plugins

### Performance Monitoring

- **Memory**: memory_profiler, tracemalloc
- **CPU**: cProfile, py-spy, pyflame
- **I/O**: iostat, iotop
- **Network**: wireshark, tcpdump (for debugging Ollama connections)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make Llamaball the fastest, most efficient document chat system available! 🦙⚡ 