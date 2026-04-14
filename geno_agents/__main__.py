import sys

if len(sys.argv) > 1 and sys.argv[1] == "mcp":
    import asyncio
    from geno_agents.mcp_server import main
    asyncio.run(main())
else:
    from geno_agents.cli import main
    main()
